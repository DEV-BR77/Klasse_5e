from __future__ import annotations

import hashlib
from io import BytesIO

import numpy as np
import onnxruntime as ort
from PIL import Image

from .imaging import validate_image


class SafetyModelUnavailable(RuntimeError):
    pass


class ImageSafetyClassifier:
    model_id = "Falconsai/nsfw_image_detection"
    revision = "96cb0d0342c7afb80cab76ecc58b265fa44da256"

    def __init__(self, model_path, expected_sha256: str, threshold: float, session=None):
        self.model_path = model_path
        self.expected_sha256 = expected_sha256.lower()
        self.threshold = threshold
        self._session = session

    def health_check(self) -> tuple[bool, str]:
        try:
            self._get_session()
        except SafetyModelUnavailable:
            return False, "model_not_installed_or_checksum_invalid"
        return True, "ready"

    def classify(self, content: bytes, *, max_bytes: int, max_pixels: int) -> dict:
        validated = validate_image(content, max_bytes=max_bytes, max_pixels=max_pixels)
        with Image.open(BytesIO(validated.jpeg_bytes)) as image:
            image = image.convert("RGB").resize((224, 224), Image.Resampling.BILINEAR)
            pixels = np.asarray(image, dtype=np.float32) / 255.0
        pixels = ((pixels - 0.5) / 0.5).transpose(2, 0, 1)[None, ...]
        session = self._get_session()
        input_name = session.get_inputs()[0].name
        logits = np.asarray(session.run(None, {input_name: pixels})[0], dtype=np.float64)[0]
        probabilities = np.exp(logits - logits.max())
        probabilities /= probabilities.sum()
        nsfw_score = float(probabilities[1])
        return {
            "decision": "blocked" if nsfw_score >= self.threshold else "approved",
            "model_id": self.model_id,
            "model_revision": self.revision,
        }

    def _get_session(self):
        if self._session is not None:
            return self._session
        if not self.expected_sha256 or not self.model_path.is_file():
            raise SafetyModelUnavailable("model_not_configured")
        digest_builder = hashlib.sha256()
        with self.model_path.open("rb") as model_file:
            for chunk in iter(lambda: model_file.read(1024 * 1024), b""):
                digest_builder.update(chunk)
        digest = digest_builder.hexdigest()
        if digest != self.expected_sha256:
            raise SafetyModelUnavailable("model_checksum_mismatch")
        try:
            self._session = ort.InferenceSession(
                str(self.model_path), providers=["CPUExecutionProvider"]
            )
        except Exception as exc:
            raise SafetyModelUnavailable("model_load_failed") from exc
        return self._session
