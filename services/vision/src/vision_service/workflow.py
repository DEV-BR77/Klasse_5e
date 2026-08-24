from __future__ import annotations

import hashlib
import uuid
from collections import defaultdict
from datetime import UTC, datetime

import cv2
import numpy as np
from sqlalchemy import delete, select

from .config import settings
from .database import SessionLocal
from .models import Collection, Embedding, Face, Image, Job, Match, Reference
from .pipelines.base import VisionPipeline, normalize_embedding
from .registry import PipelineRegistry
from .storage import Storage


def vector_bytes(vector: np.ndarray) -> bytes:
    return normalize_embedding(vector).astype("<f4", copy=False).tobytes()


def bytes_vector(value: bytes, dimension: int) -> np.ndarray:
    vector = np.frombuffer(value, dtype="<f4")
    return normalize_embedding(vector, dimension)


def process_job(
    job_collection_id: str, job_id: str, registry: PipelineRegistry, storage: Storage
) -> None:
    with SessionLocal() as session:
        job = session.get(Job, (job_collection_id, job_id))
        if job is None or job.status not in {"queued", "running"}:
            return
        if job.cancel_requested:
            job.status = "cancelled"
            job.completed_at = datetime.now(UTC)
            session.commit()
            return
        job.status = "running"
        job.started_at = job.started_at or datetime.now(UTC)
        job.error_code = None
        session.commit()
        try:
            collection = session.get(Collection, job.collection_id)
            image_row = session.get(Image, (job.collection_id, job.image_id))
            if collection is None or image_row is None:
                raise RuntimeError("resource_not_found")
            pipeline = registry.get(collection.pipeline_id)
            image = cv2.imread(str(storage.image_path(job.collection_id, image_row.image_id)))
            if image is None:
                raise RuntimeError("image_unavailable")
            session.execute(
                delete(Match).where(
                    Match.collection_id == job.collection_id,
                    Match.face_id.in_(
                        select(Face.face_id).where(
                            Face.collection_id == job.collection_id,
                            Face.image_id == image_row.image_id,
                        )
                    ),
                )
            )
            session.execute(
                delete(Face).where(
                    Face.collection_id == job.collection_id, Face.image_id == image_row.image_id
                )
            )
            session.flush()
            detections = pipeline.detect_faces(image)
            for index, detected in enumerate(detections):
                if job.cancel_requested:
                    raise RuntimeError("job_cancelled")
                face_id = _face_id(image_row.image_id, index, detected.bbox)
                aligned = pipeline.align_face(image, detected)
                vector = pipeline.create_embedding(aligned)
                crop_ok, crop_bytes = cv2.imencode(".jpg", aligned, [cv2.IMWRITE_JPEG_QUALITY, 88])
                if not crop_ok:
                    raise RuntimeError("crop_encoding_failed")
                crop_path = storage.write_crop(job.collection_id, face_id, crop_bytes.tobytes())
                face = Face(
                    collection_id=job.collection_id,
                    face_id=face_id,
                    image_id=image_row.image_id,
                    bbox={
                        "x": detected.bbox[0],
                        "y": detected.bbox[1],
                        "width": detected.bbox[2],
                        "height": detected.bbox[3],
                    },
                    landmarks=[{"x": point[0], "y": point[1]} for point in detected.landmarks],
                    detection_score=detected.score,
                    quality={
                        "aligned_width": int(aligned.shape[1]),
                        "aligned_height": int(aligned.shape[0]),
                    },
                    pipeline_id=collection.pipeline_id,
                    model_version=collection.model_version,
                    crop_name=crop_path.name,
                )
                session.add(face)
                session.add(
                    Embedding(
                        collection_id=job.collection_id,
                        embedding_id=f"face-{face_id}",
                        owner_type="face",
                        owner_id=face_id,
                        pipeline_id=collection.pipeline_id,
                        model_version=collection.model_version,
                        dimension=vector.size,
                        vector=vector_bytes(vector),
                    )
                )
                session.flush()
                _create_matches(session, pipeline, collection, face_id, vector)
                job.progress = round((index + 1) * 100 / max(len(detections), 1))
                session.commit()
            image_row.status = "analyzed"
            job.progress = 100
            job.status = "completed"
            job.completed_at = datetime.now(UTC)
            session.commit()
        except Exception as exc:
            session.rollback()
            job = session.get(Job, (job_collection_id, job_id))
            if job is not None:
                job.status = "cancelled" if str(exc) == "job_cancelled" else "failed"
                job.error_code = _safe_error(exc)
                job.completed_at = datetime.now(UTC)
                session.commit()


def resume_jobs(registry: PipelineRegistry, storage: Storage) -> None:
    with SessionLocal() as session:
        for job in session.scalars(select(Job).where(Job.status == "running")):
            job.status = "queued"
            job.error_code = "requeued_after_restart"
        session.commit()
        jobs = list(
            session.execute(select(Job.collection_id, Job.job_id).where(Job.status == "queued"))
        )
    for collection_id, job_id in jobs:
        process_job(collection_id, job_id, registry, storage)


def _create_matches(
    session, pipeline: VisionPipeline, collection: Collection, face_id: str, vector: np.ndarray
) -> None:
    references = list(
        session.execute(
            select(Reference, Embedding)
            .join(
                Embedding,
                (Embedding.collection_id == Reference.collection_id)
                & (Embedding.owner_type == "reference")
                & (Embedding.owner_id == Reference.reference_id),
            )
            .where(
                Reference.collection_id == collection.collection_id,
                Reference.confirmed.is_(True),
                Reference.revoked_at.is_(None),
                Reference.pipeline_id == collection.pipeline_id,
                Reference.model_version == collection.model_version,
                Embedding.pipeline_id == collection.pipeline_id,
                Embedding.model_version == collection.model_version,
            )
        )
    )
    grouped: dict[str, list[np.ndarray]] = defaultdict(list)
    for reference, embedding in references:
        grouped[reference.subject_id].append(bytes_vector(embedding.vector, embedding.dimension))
    ranked = []
    for subject_id, vectors in grouped.items():
        scores = [pipeline.compare_embeddings(item, vector) for item in vectors]
        centroid = normalize_embedding(np.mean(vectors, axis=0))
        score = 0.7 * max(scores) + 0.3 * pipeline.compare_embeddings(centroid, vector)
        if score >= settings.similarity_floor:
            ranked.append((subject_id, float(score)))
    ranked.sort(key=lambda item: item[1], reverse=True)
    for rank, (subject_id, score) in enumerate(ranked[: settings.max_candidates], 1):
        session.add(
            Match(
                collection_id=collection.collection_id,
                match_id=uuid.uuid4().hex,
                face_id=face_id,
                subject_id=subject_id,
                score=score,
                rank=rank,
            )
        )


def _face_id(image_id: str, index: int, bbox: tuple[int, int, int, int]) -> str:
    return hashlib.sha256(f"{image_id}|{index}|{bbox}".encode()).hexdigest()[:32]


def _safe_error(exc: Exception) -> str:
    allowed = {
        "resource_not_found",
        "image_unavailable",
        "job_cancelled",
        "crop_encoding_failed",
        "model_not_installed",
        "model_checksum_mismatch",
        "model_not_licensed_or_installed",
        "unknown_pipeline",
    }
    value = str(exc)
    return value if value in allowed else "processing_failed"
