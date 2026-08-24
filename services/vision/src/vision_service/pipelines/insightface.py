import numpy as np

from .base import DetectedFace, ModelInformation, VisionPipeline


class DisabledInsightFacePipeline(VisionPipeline):
    pipeline_id = "scrfd-arcface-disabled"

    def _disabled(self):
        raise RuntimeError("model_not_licensed_or_installed")

    def detect_faces(self, image: np.ndarray) -> list[DetectedFace]:
        return self._disabled()

    def align_face(self, image: np.ndarray, face: DetectedFace) -> np.ndarray:
        return self._disabled()

    def create_embedding(self, face: np.ndarray) -> np.ndarray:
        return self._disabled()

    def compare_embeddings(self, reference: np.ndarray, candidate: np.ndarray) -> float:
        return self._disabled()

    def model_information(self) -> ModelInformation:
        return ModelInformation(
            pipeline_id=self.pipeline_id,
            detector_name="SCRFD",
            detector_version="not installed",
            recognizer_name="ArcFace",
            recognizer_version="not installed",
            embedding_dimension=0,
            similarity_metric="cosine_similarity_when_licensed",
            model_origin="InsightFace candidate; no weights installed",
            license_identifier="written_permission_required",
            weight_checksums={},
            runtime_provider="ONNX Runtime CPU when separately licensed",
            input_size="not configured",
            status="model_not_licensed_or_installed",
        )

    def health_check(self) -> tuple[bool, str]:
        return False, "model_not_licensed_or_installed"
