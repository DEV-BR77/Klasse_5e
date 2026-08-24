from pathlib import Path

import cv2
import numpy as np
import pytest

from vision_service.pipelines.yunet_sface import YuNetSFacePipeline

ROOT = Path(__file__).parents[1]


def test_yunet_detects_synthetic_face_and_sface_embeds_it() -> None:
    pipeline = YuNetSFacePipeline(
        ROOT / "models" / "face_detection_yunet_2023mar.onnx",
        ROOT / "models" / "face_recognition_sface_2021dec.onnx",
    )
    image = cv2.imread(str(ROOT / "tests" / "fixtures" / "synthetic-adult-face.png"))
    assert image is not None
    detections = pipeline.detect_faces(image)
    assert len(detections) == 1
    aligned = pipeline.align_face(image, detections[0])
    embedding = pipeline.create_embedding(aligned)
    assert embedding.shape == (128,)
    assert np.linalg.norm(embedding) == pytest.approx(1.0, abs=1e-5)
