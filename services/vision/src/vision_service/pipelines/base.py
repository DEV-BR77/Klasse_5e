from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class DetectedFace:
    bbox: tuple[int, int, int, int]
    landmarks: tuple[tuple[float, float], ...]
    score: float


@dataclass(frozen=True, slots=True)
class ModelInformation:
    pipeline_id: str
    detector_name: str
    detector_version: str
    recognizer_name: str
    recognizer_version: str
    embedding_dimension: int
    similarity_metric: str
    model_origin: str
    license_identifier: str
    weight_checksums: dict[str, str]
    runtime_provider: str
    input_size: str
    status: str

    def as_dict(self) -> dict:
        return asdict(self)


class VisionPipeline(ABC):
    @abstractmethod
    def detect_faces(self, image: np.ndarray) -> list[DetectedFace]: ...

    @abstractmethod
    def align_face(self, image: np.ndarray, face: DetectedFace) -> np.ndarray: ...

    @abstractmethod
    def create_embedding(self, face: np.ndarray) -> np.ndarray: ...

    @abstractmethod
    def compare_embeddings(self, reference: np.ndarray, candidate: np.ndarray) -> float: ...

    @abstractmethod
    def model_information(self) -> ModelInformation: ...

    @abstractmethod
    def health_check(self) -> tuple[bool, str]: ...


def normalize_embedding(vector: np.ndarray, expected_dimension: int | None = None) -> np.ndarray:
    flattened = np.asarray(vector, dtype=np.float32).reshape(-1)
    if expected_dimension is not None and flattened.size != expected_dimension:
        raise ValueError("embedding_dimension_mismatch")
    norm = float(np.linalg.norm(flattened))
    if not np.isfinite(norm) or norm <= 0:
        raise ValueError("invalid_embedding")
    return flattened / norm


def cosine_similarity(reference: np.ndarray, candidate: np.ndarray) -> float:
    left = normalize_embedding(reference)
    right = normalize_embedding(candidate, left.size)
    return float(np.clip(np.dot(left, right), -1.0, 1.0))
