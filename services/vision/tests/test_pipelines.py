from pathlib import Path

import numpy as np
import pytest

from vision_service.manifest import ModelManifest, safe_model_path
from vision_service.pipelines.base import VisionPipeline, cosine_similarity, normalize_embedding
from vision_service.pipelines.insightface import DisabledInsightFacePipeline
from vision_service.pipelines.legacy import HaarLbphBaseline


def test_pipeline_contract_is_abstract() -> None:
    with pytest.raises(TypeError):
        VisionPipeline()


def test_normalize_embedding_has_unit_length() -> None:
    result = normalize_embedding(np.array([3.0, 4.0]), 2)
    assert np.linalg.norm(result) == pytest.approx(1.0)


def test_embedding_dimension_is_enforced() -> None:
    with pytest.raises(ValueError, match="embedding_dimension_mismatch"):
        normalize_embedding(np.array([1.0, 2.0]), 3)


def test_zero_embedding_is_rejected() -> None:
    with pytest.raises(ValueError, match="invalid_embedding"):
        normalize_embedding(np.zeros(3))


def test_cosine_similarity_orders_equal_above_different() -> None:
    reference = np.array([1.0, 0.0])
    assert cosine_similarity(reference, reference) > cosine_similarity(
        reference, np.array([0.0, 1.0])
    )


def test_manifest_loads_pinned_models() -> None:
    path = Path(__file__).parents[1] / "models" / "manifest.json"
    manifest = ModelManifest.load(path)
    assert manifest.entries["opencv-yunet-2023mar"].version == "2023mar"
    assert len(manifest.entries["opencv-sface-2021dec"].sha256) == 64


def test_manifest_checksum_validation(tmp_path: Path) -> None:
    path = Path(__file__).parents[1] / "models" / "manifest.json"
    manifest = ModelManifest.load(path)
    (tmp_path / "face_detection_yunet_2023mar.onnx").write_bytes(b"wrong")
    with pytest.raises(ValueError, match="model_checksum_mismatch"):
        manifest.verify("opencv-yunet-2023mar", tmp_path)


def test_model_path_rejects_traversal(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unsafe_model_filename"):
        safe_model_path(tmp_path, "../model.onnx")


def test_legacy_pipeline_is_clearly_baseline() -> None:
    info = HaarLbphBaseline().model_information()
    assert info.status == "legacy_baseline_only"
    assert "not_probability" in info.similarity_metric


def test_insightface_pipeline_is_disabled() -> None:
    pipeline = DisabledInsightFacePipeline()
    assert pipeline.health_check() == (False, "model_not_licensed_or_installed")
    with pytest.raises(RuntimeError, match="model_not_licensed_or_installed"):
        pipeline.detect_faces(np.zeros((10, 10, 3), dtype=np.uint8))
