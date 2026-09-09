from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    data_dir: Path = Path("/data")
    model_dir: Path = Path("/models")
    database_url: str = "sqlite:////data/vision.sqlite3"
    service_token: str = Field(default="", repr=False)
    active_pipeline: str = "yunet-sface-2023mar-2021dec"
    max_upload_bytes: int = 12 * 1024 * 1024
    max_pixels: int = 40_000_000
    max_candidates: int = 3
    similarity_floor: float = 0.0
    job_poll_seconds: float = 0.25
    model_manifest_path: Path = Path("/app/models/manifest.json")
    nsfw_model_path: Path = Path("/models/falconsai-nsfw-96cb0d0/model.onnx")
    nsfw_model_sha256: str = ""
    nsfw_block_threshold: float = 0.8

    model_config = SettingsConfigDict(env_prefix="VISION_", extra="ignore")

    @model_validator(mode="after")
    def validate_security(self) -> "Settings":
        if self.service_token and len(self.service_token) < 32:
            raise ValueError("VISION_SERVICE_TOKEN must contain at least 32 characters")
        if self.max_upload_bytes < 1024 or self.max_pixels < 1024:
            raise ValueError("image limits are too small")
        if not 0.5 <= self.nsfw_block_threshold < 1:
            raise ValueError("NSFW threshold must be between 0.5 and 1")
        return self


settings = Settings()
