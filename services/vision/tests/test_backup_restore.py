import json
import subprocess
import sys
from pathlib import Path

from conftest import TEST_ROOT, create_collection, upload_image


def test_backup_restore_to_fresh_directory(
    client, auth_headers, jpeg_bytes, tmp_path: Path
) -> None:
    create_collection(client, auth_headers)
    upload_image(client, auth_headers, jpeg_bytes)
    service = Path(__file__).parents[1]
    backup = tmp_path / "backup"
    restored = tmp_path / "restored"
    subprocess.run(
        [
            sys.executable,
            str(service / "scripts" / "backup.py"),
            "--data",
            str(TEST_ROOT / "data"),
            "--models",
            str(TEST_ROOT / "models"),
            "--manifest",
            str(service / "models" / "manifest.json"),
            "--output",
            str(backup),
        ],
        check=True,
    )
    manifest = json.loads((backup / "backup-manifest.json").read_text(encoding="utf-8"))
    assert manifest["database_revision"] == "0001"
    assert "secret://projects/klasse-5e/vision_service_token" in manifest["secret_references"]
    assert "test-service-token" not in (backup / "backup-manifest.json").read_text(encoding="utf-8")
    subprocess.run(
        [
            sys.executable,
            str(service / "scripts" / "restore.py"),
            "--backup",
            str(backup),
            "--target",
            str(restored),
        ],
        check=True,
    )
    assert (restored / "vision.sqlite3").is_file()
    assert (restored / "imports" / "collection-a" / "image-1.jpg").is_file()
