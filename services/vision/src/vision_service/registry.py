from __future__ import annotations

from pathlib import Path

from .manifest import ModelManifest
from .pipelines import (
    DisabledInsightFacePipeline,
    HaarLbphBaseline,
    VisionPipeline,
    YuNetSFacePipeline,
)


class PipelineRegistry:
    def __init__(self, manifest: ModelManifest, model_dir: Path) -> None:
        self.manifest = manifest
        self.model_dir = model_dir
        self._instances: dict[str, VisionPipeline] = {
            HaarLbphBaseline.pipeline_id: HaarLbphBaseline(),
            DisabledInsightFacePipeline.pipeline_id: DisabledInsightFacePipeline(),
        }

    def get(self, pipeline_id: str) -> VisionPipeline:
        if pipeline_id == YuNetSFacePipeline.pipeline_id and pipeline_id not in self._instances:
            yunet = self.manifest.verify("opencv-yunet-2023mar", self.model_dir)
            sface = self.manifest.verify("opencv-sface-2021dec", self.model_dir)
            self._instances[pipeline_id] = YuNetSFacePipeline(yunet, sface)
        if pipeline_id not in self._instances:
            raise KeyError("unknown_pipeline")
        return self._instances[pipeline_id]

    def information(self) -> list[dict]:
        ids = [
            YuNetSFacePipeline.pipeline_id,
            HaarLbphBaseline.pipeline_id,
            DisabledInsightFacePipeline.pipeline_id,
        ]
        result = []
        for pipeline_id in ids:
            try:
                result.append(self.get(pipeline_id).model_information().as_dict())
            except (FileNotFoundError, ValueError):
                if pipeline_id == YuNetSFacePipeline.pipeline_id:
                    result.append(
                        {
                            "pipeline_id": pipeline_id,
                            "detector_name": "YuNet",
                            "detector_version": "2023mar",
                            "recognizer_name": "SFace",
                            "recognizer_version": "2021dec",
                            "embedding_dimension": 128,
                            "similarity_metric": "cosine_similarity",
                            "model_origin": "OpenCV Zoo",
                            "license_identifier": "YuNet MIT; SFace Apache-2.0",
                            "weight_checksums": {
                                entry.model_id: entry.sha256
                                for entry in self.manifest.entries.values()
                                if entry.model_id.startswith("opencv-")
                            },
                            "runtime_provider": "OpenCV DNN CPU",
                            "input_size": "detector image size; SFace 112x112",
                            "status": "model_not_installed_or_checksum_invalid",
                        }
                    )
                else:
                    raise
        return result
