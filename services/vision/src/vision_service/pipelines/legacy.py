from pathlib import Path

import cv2
import numpy as np

from .base import (
    DetectedFace,
    ModelInformation,
    VisionPipeline,
    normalize_embedding,
)


class HaarLbphBaseline(VisionPipeline):
    """Legacy comparison baseline; its vector is not a probability or SFace-compatible."""

    pipeline_id = "haar-lbph-baseline-v1"

    def __init__(self) -> None:
        path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
        self._cascade = cv2.CascadeClassifier(str(path))

    def detect_faces(self, image: np.ndarray) -> list[DetectedFace]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        boxes = self._cascade.detectMultiScale(gray, 1.12, 5, minSize=(48, 48))
        return [DetectedFace(tuple(map(int, box)), (), 0.0) for box in boxes]

    def align_face(self, image: np.ndarray, face: DetectedFace) -> np.ndarray:
        x, y, width, height = face.bbox
        return cv2.resize(image[y : y + height, x : x + width], (128, 128))

    def create_embedding(self, face: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        center = gray[1:-1, 1:-1]
        neighbours = (
            gray[:-2, :-2],
            gray[:-2, 1:-1],
            gray[:-2, 2:],
            gray[1:-1, 2:],
            gray[2:, 2:],
            gray[2:, 1:-1],
            gray[2:, :-2],
            gray[1:-1, :-2],
        )
        lbp = np.zeros(center.shape, dtype=np.uint8)
        for bit, neighbour in enumerate(neighbours):
            lbp |= (neighbour >= center).astype(np.uint8) << bit
        parts: list[np.ndarray] = []
        for row in np.array_split(lbp, 8, axis=0):
            for cell in np.array_split(row, 8, axis=1):
                histogram = np.bincount(cell.ravel(), minlength=256).astype(np.float32)
                total = float(histogram.sum())
                parts.append(histogram / total if total else histogram)
        return normalize_embedding(np.concatenate(parts), 8 * 8 * 256)

    def compare_embeddings(self, reference: np.ndarray, candidate: np.ndarray) -> float:
        if reference.shape != candidate.shape:
            raise ValueError("embedding_dimension_mismatch")
        denominator = reference + candidate + 1e-12
        distance = 0.5 * float(np.sum(((reference - candidate) ** 2) / denominator))
        return 1.0 / (1.0 + distance)

    def model_information(self) -> ModelInformation:
        return ModelInformation(
            pipeline_id=self.pipeline_id,
            detector_name="OpenCV Haar Cascade",
            detector_version=cv2.__version__,
            recognizer_name="Local Binary Pattern Histograms (8x8 grid)",
            recognizer_version="v1",
            embedding_dimension=16384,
            similarity_metric="inverse_chi_square_distance_not_probability",
            model_origin="OpenCV packaged cascade",
            license_identifier="Apache-2.0 (OpenCV distribution)",
            weight_checksums={},
            runtime_provider="OpenCV CPU",
            input_size="128x128 grayscale crop",
            status="legacy_baseline_only",
        )

    def health_check(self) -> tuple[bool, str]:
        return (
            not self._cascade.empty(),
            "ready" if not self._cascade.empty() else "model_missing",
        )
