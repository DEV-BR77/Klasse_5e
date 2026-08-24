from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

SCHEMA_REVISION = "0001"


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--models", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("output already exists")
    args.output.mkdir(parents=True)
    files_dir = args.output / "data"
    files_dir.mkdir()
    source_db = args.data / "vision.sqlite3"
    target_db = files_dir / "vision.sqlite3"
    with sqlite3.connect(source_db) as source, sqlite3.connect(target_db) as target:
        source.backup(target)
    for name in ("imports", "crops"):
        source = args.data / name
        if source.exists():
            shutil.copytree(source, files_dir / name)
    shutil.copy2(args.manifest, args.output / "model-manifest.json")
    checksums = {}
    for path in sorted(args.output.rglob("*")):
        if path.is_file() and path.name != "backup-manifest.json":
            checksums[path.relative_to(args.output).as_posix()] = hash_file(path)
    backup_manifest = {
        "schema_version": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "database_revision": SCHEMA_REVISION,
        "model_files_present": sorted(path.name for path in args.models.glob("*.onnx")),
        "secret_references": ["secret://projects/klasse-5e/vision_service_token"],
        "checksums": checksums,
    }
    (args.output / "backup-manifest.json").write_text(
        json.dumps(backup_manifest, indent=2, sort_keys=True), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
