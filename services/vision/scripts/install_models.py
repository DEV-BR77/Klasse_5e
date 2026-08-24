"""Explicitly download approved models and verify the pinned manifest hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("models/manifest.json"))
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--offline-source", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    args.target.mkdir(parents=True, exist_ok=True)
    for model in manifest["models"]:
        if not model["usage_status"].startswith("approved_"):
            continue
        target = args.target / model["filename"]
        temporary = target.with_suffix(target.suffix + ".part")
        if args.offline_source:
            source = args.offline_source / model["filename"]
            temporary.write_bytes(source.read_bytes())
        else:
            with urllib.request.urlopen(model["source_url"], timeout=60) as response:
                temporary.write_bytes(response.read())
        digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
        if digest != model["sha256"]:
            temporary.unlink(missing_ok=True)
            raise SystemExit(f"checksum mismatch for {model['model_id']}")
        temporary.replace(target)
        print(f"installed {model['model_id']} ({digest})")


if __name__ == "__main__":
    main()
