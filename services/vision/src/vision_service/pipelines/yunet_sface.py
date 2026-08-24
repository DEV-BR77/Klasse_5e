from pathlib import Path

import cv2
import numpy as np

from .base import (
    DetectedFace,
    ModelInformation,
    VisionPipeline,
    cosine_similarity,
    normalize_embedding,
)


class YuNetSFacePipeline(VisionPipeline):
    pipeline_id = "yunet-sface-2023mar-2021dec"

    def __init__(self, yunet_path: Path, sface_path: Path) -> None:
        self._detector = cv2.FaceDetectorYN.create(
            str(yunet_path),
            "",
            (320, 320),
            0.75,
            0.3,
            5000,
            cv2.dnn.DNN_BACKEND_OPENCV,
            cv2.dnn.DNN_TARGET_CPU,
        )
        self._recognizer = cv2.FaceRecognizerSF.create(
            str(sface_path), "", cv2.dnn.DNN_BACKEND_OPENCV, cv2.dnn.DNN_TARGET_CPU
        )
        self._checksums = {
            "opencv-yunet-2023mar": (
                "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4"
            ),
            "opencv-sface-2021dec": (
                "0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79"
            ),
        }

    def detect_faces(self, image: np.ndarray) -> list[DetectedFace]:
        height, width = image.shape[:2]
        self._detector.setInputSize((width, height))
        _code, rows = self._detector.detect(image)
        if rows is None:
            return []
        return [
            DetectedFace(
                bbox=tuple(int(value) for value in row[:4]),
                landmarks=tuple(
                    (float(row[index]), float(row[index + 1])) for index in range(4, 14, 2)
                ),
                score=float(row[14]),
            )
            for row in rows
        ]

    def align_face(self, image: np.ndarray, face: DetectedFace) -> np.ndarray:
        row = np.asarray(
            [
                *face.bbox,
                *(coordinate for point in face.landmarks for coordinate in point),
                face.score,
            ],
            dtype=np.float32,
        )
        return self._recognizer.alignCrop(image, row)

    def create_embedding(self, face: np.ndarray) -> np.ndarray:
        return normalize_embedding(self._recognizer.feature(face), 128)

    def compare_embeddings(self, reference: np.ndarray, candidate: np.ndarray) -> float:
        return cosine_similarity(reference, candidate)

    def model_information(self) -> ModelInformation:
        return ModelInformation(
            pipeline_id=self.pipeline_id,
            detector_name="YuNet",
            detector_version="2023mar",
            recognizer_name="SFace",
            recognizer_version="2021dec",
            embedding_dimension=128,
            similarity_metric="cosine_similarity",
            model_origin="OpenCV Zoo",
            license_identifier="YuNet MIT; SFace Apache-2.0",
            weight_checksums=self._checksums,
            runtime_provider=(
                "OpenCV DNN CPU (ONNX models); ONNX Runtime CPU packaged for optional adapters"
            ),
            input_size="detector=image dimensions; recognizer=112x112 aligned face",
            status="available",
        )

    def health_check(self) -> tuple[bool, str]:
        return True, "ready"
