FROM python:3.12.10-slim-bookworm@sha256:fd95fa221297a88e1cf49c55ec1828edd7c5a428187e67b5d1805692d11588db

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VISION_DATA_DIR=/data \
    VISION_MODEL_DIR=/models \
    VISION_MODEL_MANIFEST_PATH=/app/models/manifest.json

RUN groupadd --system --gid 10001 vision \
    && useradd --system --uid 10001 --gid vision --home-dir /nonexistent --shell /usr/sbin/nologin vision

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY migrations ./migrations
COPY scripts ./scripts
COPY alembic.ini ./
COPY models/manifest.json ./models/manifest.json
COPY docker/entrypoint.sh /usr/local/bin/vision-entrypoint
RUN python -m pip install . \
    && chmod 0555 /usr/local/bin/vision-entrypoint \
    && mkdir -p /data /models /tmp/vision \
    && chown -R vision:vision /data /models /tmp/vision

USER 10001:10001
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=6 \
  CMD python -c "import json,urllib.request; data=json.load(urllib.request.urlopen('http://127.0.0.1:8000/v1/health',timeout=2)); raise SystemExit(0 if data['status']=='ok' else 1)"
ENTRYPOINT ["/usr/local/bin/vision-entrypoint"]
