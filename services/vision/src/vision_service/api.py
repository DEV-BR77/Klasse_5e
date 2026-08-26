from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .auth import require_service_token
from .config import settings
from .database import get_session
from .imaging import ImageValidationError, validate_image
from .models import (
    Collection,
    Embedding,
    Face,
    IdempotencyRecord,
    Image,
    Job,
    Match,
    Reference,
    Subject,
)
from .schemas import (
    CollectionCreate,
    CollectionRead,
    DecisionRequest,
    DeleteResult,
    DismissRequest,
    FaceRead,
    ImageRead,
    JobRead,
    MatchRead,
    ReferenceCreate,
    ReferenceRead,
    RejectRequest,
    SubjectCreate,
    SubjectRead,
)
from .workflow import process_job

DatabaseSession = Annotated[Session, Depends(get_session)]
router = APIRouter(prefix="/v1", dependencies=[Depends(require_service_token)])


def resources():
    from .main import registry, storage

    return registry, storage


def hidden_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="resource_not_found")


@router.get("/models")
def list_models() -> list[dict]:
    registry, _ = resources()
    return registry.information()


@router.get("/models/{pipeline_id}")
def get_model(pipeline_id: str) -> dict:
    result = next((item for item in list_models() if item["pipeline_id"] == pipeline_id), None)
    if result is None:
        raise hidden_not_found()
    return result


@router.post("/collections", response_model=CollectionRead, status_code=201)
def create_collection(data: CollectionCreate, db: DatabaseSession) -> Collection:
    existing = db.get(Collection, data.collection_id)
    if existing:
        if existing.pipeline_id != data.pipeline_id:
            raise HTTPException(status_code=409, detail="collection_conflict")
        return existing
    registry, _ = resources()
    info = get_model(data.pipeline_id)
    if info["status"] != "available" and data.pipeline_id != "haar-lbph-baseline-v1":
        raise HTTPException(status_code=409, detail=info["status"])
    model_version = f"{info['detector_version']}+{info['recognizer_version']}"
    item = Collection(
        collection_id=data.collection_id, pipeline_id=data.pipeline_id, model_version=model_version
    )
    db.add(item)
    db.commit()
    return item


@router.get("/collections/{collection_id}", response_model=CollectionRead)
def get_collection(collection_id: str, db: DatabaseSession) -> Collection:
    item = db.get(Collection, collection_id)
    if item is None:
        raise hidden_not_found()
    return item


@router.delete("/collections/{collection_id}", response_model=DeleteResult)
def delete_collection(collection_id: str, db: DatabaseSession) -> DeleteResult:
    _, storage = resources()
    item = db.get(Collection, collection_id)
    if item is None:
        storage.cleanup_trash()
        return DeleteResult()
    staged = storage.stage_collection_delete(collection_id)
    try:
        db.execute(delete(Embedding).where(Embedding.collection_id == collection_id))
        db.delete(item)
        db.commit()
    except Exception:
        db.rollback()
        storage.restore(staged)
        raise HTTPException(status_code=500, detail="deletion_failed") from None
    storage.finalize(staged)
    return DeleteResult()


@router.post("/collections/{collection_id}/subjects", response_model=SubjectRead, status_code=201)
def create_subject(collection_id: str, data: SubjectCreate, db: DatabaseSession) -> Subject:
    if db.get(Collection, collection_id) is None:
        raise hidden_not_found()
    item = db.get(Subject, (collection_id, data.subject_id))
    if item is None:
        item = Subject(collection_id=collection_id, subject_id=data.subject_id)
        db.add(item)
        db.commit()
    return item


@router.get("/collections/{collection_id}/subjects/{subject_id}", response_model=SubjectRead)
def get_subject(collection_id: str, subject_id: str, db: DatabaseSession) -> Subject:
    item = db.get(Subject, (collection_id, subject_id))
    if item is None:
        raise hidden_not_found()
    return item


@router.delete("/collections/{collection_id}/subjects/{subject_id}", response_model=DeleteResult)
def delete_subject(collection_id: str, subject_id: str, db: DatabaseSession) -> DeleteResult:
    item = db.get(Subject, (collection_id, subject_id))
    if item is None:
        return DeleteResult()
    reference_ids = list(
        db.scalars(
            select(Reference.reference_id).where(
                Reference.collection_id == collection_id, Reference.subject_id == subject_id
            )
        )
    )
    if reference_ids:
        db.execute(
            delete(Embedding).where(
                Embedding.collection_id == collection_id,
                Embedding.owner_type == "reference",
                Embedding.owner_id.in_(reference_ids),
            )
        )
    db.delete(item)
    db.commit()
    return DeleteResult()


@router.post("/collections/{collection_id}/images", response_model=ImageRead, status_code=201)
async def create_image(
    collection_id: str,
    db: DatabaseSession,
    image_id: Annotated[str, Header(alias="X-Image-Id")],
    file: Annotated[UploadFile, File()],
    media_reference: Annotated[str | None, Header(alias="X-Media-Reference")] = None,
) -> Image:
    if db.get(Collection, collection_id) is None:
        raise hidden_not_found()
    existing = db.get(Image, (collection_id, image_id))
    if existing:
        return existing
    try:
        validated = validate_image(
            await file.read(settings.max_upload_bytes + 1),
            max_bytes=settings.max_upload_bytes,
            max_pixels=settings.max_pixels,
        )
    except ImageValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    _, storage = resources()
    path = storage.write_image(collection_id, image_id, validated.jpeg_bytes)
    item = Image(
        collection_id=collection_id,
        image_id=image_id,
        media_reference=media_reference,
        storage_name=path.name,
        sha256=validated.sha256,
        width=validated.width,
        height=validated.height,
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=409, detail="duplicate_image") from None
    return item


@router.get("/collections/{collection_id}/images/{image_id}", response_model=ImageRead)
def get_image(collection_id: str, image_id: str, db: DatabaseSession) -> Image:
    item = db.get(Image, (collection_id, image_id))
    if item is None:
        raise hidden_not_found()
    return item


@router.post(
    "/collections/{collection_id}/images/{image_id}/purge-source", response_model=DeleteResult
)
def purge_image_source(collection_id: str, image_id: str, db: DatabaseSession) -> DeleteResult:
    """Remove the imported source after analysis while retaining derived records.

    This is deliberately separate from image deletion so an integrating application can
    enforce a short source retention period without destroying reviewed embeddings.
    """
    item = db.get(Image, (collection_id, image_id))
    if item is None:
        return DeleteResult()
    if item.status not in {"analyzed", "uploaded"}:
        raise HTTPException(status_code=409, detail="image_processing_incomplete")
    _, storage = resources()
    storage.image_path(collection_id, image_id).unlink(missing_ok=True)
    return DeleteResult()


@router.delete("/collections/{collection_id}/images/{image_id}", response_model=DeleteResult)
def delete_image(collection_id: str, image_id: str, db: DatabaseSession) -> DeleteResult:
    item = db.get(Image, (collection_id, image_id))
    if item is None:
        return DeleteResult()
    face_ids = list(
        db.scalars(
            select(Face.face_id).where(
                Face.collection_id == collection_id, Face.image_id == image_id
            )
        )
    )
    _, storage = resources()
    staged = storage.stage_image_delete(collection_id, image_id, face_ids)
    reference_ids = list(
        db.scalars(
            select(Reference.reference_id).where(
                Reference.collection_id == collection_id,
                Reference.face_id.in_(face_ids),
            )
        )
    )
    db.execute(
        delete(Embedding).where(
            Embedding.collection_id == collection_id,
            (
                ((Embedding.owner_type == "face") & Embedding.owner_id.in_(face_ids))
                | ((Embedding.owner_type == "reference") & Embedding.owner_id.in_(reference_ids))
            ),
        )
    )
    db.delete(item)
    db.commit()
    storage.finalize(staged)
    return DeleteResult()


@router.post(
    "/collections/{collection_id}/images/{image_id}/analyze",
    response_model=JobRead,
    status_code=202,
)
def analyze_image(
    collection_id: str,
    image_id: str,
    db: DatabaseSession,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
) -> Job:
    image = db.get(Image, (collection_id, image_id))
    collection = db.get(Collection, collection_id)
    if image is None or collection is None:
        raise hidden_not_found()
    record = db.get(IdempotencyRecord, (collection_id, "analyze", idempotency_key))
    if record:
        return db.get(Job, (collection_id, record.resource_id))
    job = Job(
        collection_id=collection_id,
        job_id=uuid.uuid4().hex,
        image_id=image_id,
        type="analyze_image",
        pipeline_id=collection.pipeline_id,
        model_version=collection.model_version,
    )
    db.add(job)
    db.add(
        IdempotencyRecord(
            collection_id=collection_id,
            operation="analyze",
            key=idempotency_key,
            resource_id=job.job_id,
        )
    )
    db.commit()
    registry, storage = resources()
    process_job(collection_id, job.job_id, registry, storage)
    db.refresh(job)
    return job


@router.get("/collections/{collection_id}/jobs/{job_id}", response_model=JobRead)
def get_job(collection_id: str, job_id: str, db: DatabaseSession) -> Job:
    item = db.get(Job, (collection_id, job_id))
    if item is None:
        raise hidden_not_found()
    return item


@router.post("/collections/{collection_id}/jobs/{job_id}/cancel", response_model=JobRead)
def cancel_job(collection_id: str, job_id: str, db: DatabaseSession) -> Job:
    item = get_job(collection_id, job_id, db)
    if item.status in {"completed", "failed", "cancelled"}:
        return item
    item.cancel_requested = True
    if item.status == "queued":
        item.status = "cancelled"
        item.completed_at = datetime.now(UTC)
    db.commit()
    return item


@router.get("/collections/{collection_id}/images/{image_id}/faces", response_model=list[FaceRead])
def list_faces(collection_id: str, image_id: str, db: DatabaseSession) -> list[Face]:
    if db.get(Image, (collection_id, image_id)) is None:
        raise hidden_not_found()
    return list(
        db.scalars(
            select(Face).where(Face.collection_id == collection_id, Face.image_id == image_id)
        )
    )


@router.get("/collections/{collection_id}/faces/{face_id}/matches", response_model=list[MatchRead])
def list_matches(collection_id: str, face_id: str, db: DatabaseSession) -> list[Match]:
    if db.get(Face, (collection_id, face_id)) is None:
        raise hidden_not_found()
    return list(
        db.scalars(
            select(Match)
            .where(Match.collection_id == collection_id, Match.face_id == face_id)
            .order_by(Match.rank)
        )
    )


@router.post("/collections/{collection_id}/matches/{match_id}/confirm", response_model=MatchRead)
def confirm_match(
    collection_id: str, match_id: str, data: DecisionRequest, db: DatabaseSession
) -> Match:
    item = db.get(Match, (collection_id, match_id))
    if item is None:
        raise hidden_not_found()
    if item.status == "confirmed" and item.actor_id == data.actor_id:
        return item
    if item.status != "proposed":
        raise HTTPException(status_code=409, detail="decision_conflict")
    item.status, item.actor_id, item.decided_at = "confirmed", data.actor_id, datetime.now(UTC)
    db.execute(
        delete(Match).where(
            Match.collection_id == collection_id,
            Match.face_id == item.face_id,
            Match.match_id != item.match_id,
            Match.status == "proposed",
        )
    )
    if data.add_as_reference:
        _add_reference(
            db, collection_id, item.subject_id, f"confirmed-{item.match_id}", item.face_id
        )
    db.commit()
    return item


@router.post("/collections/{collection_id}/matches/{match_id}/reject", response_model=MatchRead)
def reject_match(
    collection_id: str, match_id: str, data: RejectRequest, db: DatabaseSession
) -> Match:
    item = db.get(Match, (collection_id, match_id))
    if item is None:
        raise hidden_not_found()
    if item.status == "rejected" and item.actor_id == data.actor_id:
        return item
    if item.status != "proposed":
        raise HTTPException(status_code=409, detail="decision_conflict")
    item.status, item.actor_id, item.decided_at = "rejected", data.actor_id, datetime.now(UTC)
    db.commit()
    return item


@router.post("/collections/{collection_id}/faces/{face_id}/dismiss", response_model=FaceRead)
def dismiss_face(
    collection_id: str, face_id: str, data: DismissRequest, db: DatabaseSession
) -> Face:
    item = db.get(Face, (collection_id, face_id))
    if item is None:
        raise hidden_not_found()
    if item.status == "not_a_face" and item.actor_id == data.actor_id:
        return item
    if item.status != "detected":
        raise HTTPException(status_code=409, detail="decision_conflict")
    item.status, item.actor_id, item.decided_at = "not_a_face", data.actor_id, datetime.now(UTC)
    db.execute(delete(Match).where(Match.collection_id == collection_id, Match.face_id == face_id))
    db.execute(
        delete(Embedding).where(
            Embedding.collection_id == collection_id,
            Embedding.owner_type == "face",
            Embedding.owner_id == face_id,
        )
    )
    _, storage = resources()
    storage.crop_path(collection_id, face_id).unlink(missing_ok=True)
    db.commit()
    return item


@router.post(
    "/collections/{collection_id}/subjects/{subject_id}/references",
    response_model=ReferenceRead,
    status_code=201,
)
def create_reference(
    collection_id: str, subject_id: str, data: ReferenceCreate, db: DatabaseSession
) -> Reference:
    item = _add_reference(db, collection_id, subject_id, data.reference_id, data.face_id)
    db.commit()
    return item


def _add_reference(
    db: Session, collection_id: str, subject_id: str, reference_id: str, face_id: str
) -> Reference:
    if (
        db.get(Subject, (collection_id, subject_id)) is None
        or db.get(Face, (collection_id, face_id)) is None
    ):
        raise hidden_not_found()
    existing = db.get(Reference, (collection_id, reference_id))
    if existing:
        if existing.subject_id != subject_id or existing.face_id != face_id:
            raise HTTPException(status_code=409, detail="reference_conflict")
        return existing
    face = db.get(Face, (collection_id, face_id))
    source = db.scalar(
        select(Embedding).where(
            Embedding.collection_id == collection_id,
            Embedding.owner_type == "face",
            Embedding.owner_id == face_id,
        )
    )
    if source is None or face.status != "detected":
        raise HTTPException(status_code=409, detail="face_not_reference_eligible")
    item = Reference(
        collection_id=collection_id,
        reference_id=reference_id,
        subject_id=subject_id,
        face_id=face_id,
        pipeline_id=face.pipeline_id,
        model_version=face.model_version,
    )
    db.add(item)
    db.add(
        Embedding(
            collection_id=collection_id,
            embedding_id=f"reference-{reference_id}",
            owner_type="reference",
            owner_id=reference_id,
            pipeline_id=source.pipeline_id,
            model_version=source.model_version,
            dimension=source.dimension,
            vector=source.vector,
        )
    )
    return item


@router.get(
    "/collections/{collection_id}/subjects/{subject_id}/references",
    response_model=list[ReferenceRead],
)
def list_references(collection_id: str, subject_id: str, db: DatabaseSession) -> list[Reference]:
    if db.get(Subject, (collection_id, subject_id)) is None:
        raise hidden_not_found()
    return list(
        db.scalars(
            select(Reference).where(
                Reference.collection_id == collection_id,
                Reference.subject_id == subject_id,
                Reference.revoked_at.is_(None),
            )
        )
    )


@router.delete(
    "/collections/{collection_id}/subjects/{subject_id}/references/{reference_id}",
    response_model=DeleteResult,
)
def delete_reference(
    collection_id: str, subject_id: str, reference_id: str, db: DatabaseSession
) -> DeleteResult:
    item = db.get(Reference, (collection_id, reference_id))
    if item is None:
        return DeleteResult()
    if item.subject_id != subject_id:
        raise hidden_not_found()
    db.execute(
        delete(Embedding).where(
            Embedding.collection_id == collection_id,
            Embedding.owner_type == "reference",
            Embedding.owner_id == reference_id,
        )
    )
    db.delete(item)
    db.commit()
    return DeleteResult()
