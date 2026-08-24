from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.backup / "backup-manifest.json").read_text(encoding="utf-8"))
    for relative, expected in manifest["checksums"].items():
        if hash_file(args.backup / relative) != expected:
            raise SystemExit(f"backup checksum mismatch: {relative}")
    if args.target.exists() and any(args.target.iterdir()):
        raise SystemExit("restore target must be empty")
    args.target.mkdir(parents=True, exist_ok=True)
    for path in (args.backup / "data").iterdir():
        target = args.target / path.name
        shutil.copytree(path, target) if path.is_dir() else shutil.copy2(path, target)


if __name__ == "__main__":
    main()
