import os
import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

TEST_ROOT = Path(tempfile.mkdtemp(prefix="klasse5e-vision-tests-"))
os.environ.update(
    {
        "VISION_DATA_DIR": str(TEST_ROOT / "data"),
        "VISION_MODEL_DIR": str(TEST_ROOT / "models"),
        "VISION_DATABASE_URL": f"sqlite:///{(TEST_ROOT / 'data' / 'vision.sqlite3').as_posix()}",
        "VISION_SERVICE_TOKEN": "test-service-token-with-at-least-32-characters",
        "VISION_ACTIVE_PIPELINE": "synthetic-test-v1",
        "VISION_MODEL_MANIFEST_PATH": str(Path(__file__).parents[1] / "models" / "manifest.json"),
    }
)
(TEST_ROOT / "data").mkdir(parents=True)
(TEST_ROOT / "models").mkdir(parents=True)

import vision_service.main as main_module  # noqa: E402
from vision_service.database import Base, engine  # noqa: E402
from vision_service.main import app  # noqa: E402
from vision_service.pipelines.base import (  # noqa: E402
    DetectedFace,
    ModelInformation,
    VisionPipeline,
    cosine_similarity,
    normalize_embedding,
)
from vision_service.storage import Storage  # noqa: E402


class SyntheticPipeline(VisionPipeline):
    pipeline_id = "synthetic-test-v1"

    def detect_faces(self, image):
        height, width = image.shape[:2]
        return [DetectedFace((width // 4, height // 4, width // 2, height // 2), (), 0.8)]

    def align_face(self, image, face):
        x, y, width, height = face.bbox
        return cv2.resize(image[y : y + height, x : x + width], (32, 32))

    def create_embedding(self, face):
        means = face.mean(axis=(0, 1)).astype(np.float32)
        return normalize_embedding(np.tile(means, 4), 12)

    def compare_embeddings(self, reference, candidate):
        return cosine_similarity(reference, candidate)

    def model_information(self):
        return ModelInformation(
            pipeline_id=self.pipeline_id,
            detector_name="synthetic",
            detector_version="1",
            recognizer_name="synthetic",
            recognizer_version="1",
            embedding_dimension=12,
            similarity_metric="cosine_similarity",
            model_origin="test double",
            license_identifier="generated-test-only",
            weight_checksums={},
            runtime_provider="numpy CPU",
            input_size="32x32",
            status="available",
        )

    def health_check(self):
        return True, "ready"


class SyntheticRegistry:
    def __init__(self):
        self.pipeline = SyntheticPipeline()

    def get(self, pipeline_id):
        if pipeline_id != self.pipeline.pipeline_id:
            raise KeyError("unknown_pipeline")
        return self.pipeline

    def information(self):
        return [self.pipeline.model_information().as_dict()]


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    main_module.registry = SyntheticRegistry()
    main_module.storage = Storage(TEST_ROOT / "data")
    main_module.storage.cleanup_trash()
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-service-token-with-at-least-32-characters"}


@pytest.fixture
def jpeg_bytes():
    image = np.zeros((100, 120, 3), dtype=np.uint8)
    image[:, :] = (30, 100, 220)
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok
    return encoded.tobytes()


def create_collection(client, headers, collection_id="collection-a"):
    response = client.post(
        "/v1/collections",
        headers=headers,
        json={"collection_id": collection_id, "pipeline_id": "synthetic-test-v1"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def upload_image(client, headers, content, collection_id="collection-a", image_id="image-1"):
    response = client.post(
        f"/v1/collections/{collection_id}/images",
        headers={**headers, "X-Image-Id": image_id},
        files={"file": ("upload.jpg", content, "image/jpeg")},
    )
    assert response.status_code == 201, response.text
    return response.json()


def analyze(client, headers, collection_id="collection-a", image_id="image-1", key="analysis-1"):
    response = client.post(
        f"/v1/collections/{collection_id}/images/{image_id}/analyze",
        headers={**headers, "Idempotency-Key": key},
    )
    assert response.status_code == 202, response.text
    return response.json()
