# Lokale Vision-API

Projektneutraler, ausschließlich lokal betriebener Dienst für Gesichtserkennung,
Embeddings und menschlich bestätigte Kandidaten. Er kennt nur opaque IDs. Kein
Treffer wird automatisch endgültig zugeordnet.

## Entwicklung und Tests

Python 3.12 ist nur für Pakettests hilfreich; der reguläre Betrieb erfolgt per
Docker. `python -m pytest`, `ruff check .` und `ruff format --check .` prüfen das
Paket. Modelle werden bewusst separat installiert:

```text
python scripts/install_models.py --target models
```

Der normale Start veröffentlicht keinen Port:

```text
VISION_SERVICE_TOKEN=<aus-secret-store> docker compose up --build -d
```

Nur zur lokalen Diagnose bindet `docker compose -f compose.yaml -f
compose.dev.yaml up` Port 8091 an `127.0.0.1`. Modelle liegen im benannten
Volume `klasse-5e-vision-models`, Daten in `klasse-5e-vision-data`. Der Token
wird später über `secret://klasse-5e/vision/service-token` bereitgestellt.

Details: [API](docs/API.md), [Modelle](docs/MODELS.md),
[Sicherheit](docs/SECURITY.md), [Backup/Restore](docs/BACKUP_RESTORE.md) und
[Benchmark](docs/BENCHMARK.md).
