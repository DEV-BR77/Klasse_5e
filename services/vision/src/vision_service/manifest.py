from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ModelEntry:
    model_id: str
    version: str
    source_url: str
    filename: str
    sha256: str
    license: str
    license_url: str
    origin: str
    input: str
    task: str
    usage_status: str
    runtime: str


class ModelManifest:
    def __init__(self, entries: list[ModelEntry]) -> None:
        ids = [entry.model_id for entry in entries]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate_model_id")
        self.entries = {entry.model_id: entry for entry in entries}

    @classmethod
    def load(cls, path: Path) -> ModelManifest:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw.get("schema_version") != 1 or not isinstance(raw.get("models"), list):
            raise ValueError("invalid_model_manifest")
        return cls([ModelEntry(**item) for item in raw["models"]])

    def verify(self, model_id: str, model_dir: Path) -> Path:
        entry = self.entries[model_id]
        if not entry.filename or not entry.sha256:
            raise ValueError("model_not_licensed_or_installed")
        path = safe_model_path(model_dir, entry.filename)
        if not path.is_file():
            raise FileNotFoundError("model_not_installed")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != entry.sha256:
            raise ValueError("model_checksum_mismatch")
        return path


def safe_model_path(root: Path, filename: str) -> Path:
    if Path(filename).name != filename or not filename:
        raise ValueError("unsafe_model_filename")
    resolved_root = root.resolve()
    candidate = (resolved_root / filename).resolve()
    if candidate.parent != resolved_root:
        raise ValueError("unsafe_model_path")
    return candidate
