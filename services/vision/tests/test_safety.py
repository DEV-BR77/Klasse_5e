from pathlib import Path

import numpy as np

import vision_service.main as main_module
from vision_service.safety import ImageSafetyClassifier, SafetyModelUnavailable


class _Input:
    name = "pixel_values"


class FakeSession:
    def __init__(self, logits):
        self.logits = logits

    def get_inputs(self):
        return [_Input()]

    def run(self, _outputs, inputs):
        values = inputs["pixel_values"]
        assert values.shape == (1, 3, 224, 224)
        assert values.dtype == np.float32
        return [np.array([self.logits], dtype=np.float32)]


def classifier(logits):
    return ImageSafetyClassifier(Path("unused.onnx"), "", 0.8, session=FakeSession(logits))


def test_classifier_returns_only_decision_and_pinned_model(jpeg_bytes):
    result = classifier([4.0, -2.0]).classify(jpeg_bytes, max_bytes=1_000_000, max_pixels=1_000_000)

    assert result == {
        "decision": "approved",
        "model_id": "Falconsai/nsfw_image_detection",
        "model_revision": "96cb0d0342c7afb80cab76ecc58b265fa44da256",
    }


def test_classifier_blocks_above_threshold_without_returning_score(jpeg_bytes):
    result = classifier([-2.0, 4.0]).classify(jpeg_bytes, max_bytes=1_000_000, max_pixels=1_000_000)

    assert result["decision"] == "blocked"
    assert "score" not in result


def test_safety_endpoint_is_authenticated_and_minimal(
    client, auth_headers, jpeg_bytes, monkeypatch
):
    monkeypatch.setattr(main_module, "image_safety", classifier([4.0, -2.0]))
    files = {"file": ("bild.jpg", jpeg_bytes, "image/jpeg")}

    assert client.post("/v1/safety/images/classify", files=files).status_code == 401
    response = client.post("/v1/safety/images/classify", headers=auth_headers, files=files)

    assert response.status_code == 200
    assert set(response.json()) == {"decision", "model_id", "model_revision"}


def test_safety_endpoint_fails_closed_when_model_is_unavailable(
    client, auth_headers, jpeg_bytes, monkeypatch
):
    class Unavailable:
        def classify(self, *_args, **_kwargs):
            raise SafetyModelUnavailable("synthetic")

    monkeypatch.setattr(main_module, "image_safety", Unavailable())
    response = client.post(
        "/v1/safety/images/classify",
        headers=auth_headers,
        files={"file": ("bild.jpg", jpeg_bytes, "image/jpeg")},
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "image_safety_unavailable"}
