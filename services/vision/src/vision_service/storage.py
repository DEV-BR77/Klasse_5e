from __future__ import annotations

import shutil
import uuid
from pathlib import Path


class Storage:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.imports = self.root / "imports"
        self.crops = self.root / "crops"
        self.trash = self.root / "trash"
        for directory in (self.imports, self.crops, self.trash):
            directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _id(value: str) -> str:
        if not value or any(
            character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
            for character in value
        ):
            raise ValueError("unsafe_identifier")
        return value

    def image_path(self, collection_id: str, image_id: str) -> Path:
        return self.imports / self._id(collection_id) / f"{self._id(image_id)}.jpg"

    def crop_path(self, collection_id: str, face_id: str) -> Path:
        return self.crops / self._id(collection_id) / f"{self._id(face_id)}.jpg"

    def write_image(self, collection_id: str, image_id: str, data: bytes) -> Path:
        path = self.image_path(collection_id, image_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write(path, data)
        return path

    def write_crop(self, collection_id: str, face_id: str, data: bytes) -> Path:
        path = self.crop_path(collection_id, face_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write(path, data)
        return path

    def stage_image_delete(
        self, collection_id: str, image_id: str, face_ids: list[str]
    ) -> list[Path]:
        paths = [self.image_path(collection_id, image_id)]
        paths.extend(self.crop_path(collection_id, face_id) for face_id in face_ids)
        return self._stage(paths)

    def stage_subject_delete(self, collection_id: str, face_ids: list[str]) -> list[Path]:
        return self._stage([self.crop_path(collection_id, face_id) for face_id in face_ids])

    def stage_collection_delete(self, collection_id: str) -> list[Path]:
        paths = [self.imports / self._id(collection_id), self.crops / self._id(collection_id)]
        return self._stage(paths)

    def _stage(self, paths: list[Path]) -> list[Path]:
        staged: list[Path] = []
        self.trash.mkdir(parents=True, exist_ok=True)
        for path in paths:
            if path.exists():
                target = self.trash / f"{uuid.uuid4().hex}-{path.name}"
                path.replace(target)
                staged.append(target)
        return staged

    def finalize(self, staged: list[Path]) -> None:
        for path in staged:
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                path.unlink(missing_ok=True)

    def restore(self, staged: list[Path]) -> None:
        # Staged names deliberately do not retain paths. A transaction failure is
        # reported and cleanup is repeatable; imported originals can be submitted again.
        # Keeping biometric data in trash is safer than silently restoring to a wrong owner.
        del staged

    def cleanup_trash(self) -> None:
        self.finalize(list(self.trash.iterdir()) if self.trash.exists() else [])


def _atomic_write(path: Path, data: bytes) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)
