FROM python:3.12.10-slim-bookworm@sha256:fd95fa221297a88e1cf49c55ec1828edd7c5a428187e67b5d1805692d11588db

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN groupadd --system --gid 10001 klasse5e && useradd --system --uid 10001 --gid klasse5e --home-dir /nonexistent --shell /usr/sbin/nologin klasse5e
WORKDIR /srv/app
COPY packages/web-push-kit /packages/web-push-kit
COPY app /srv/app
RUN python -m pip install /packages/web-push-kit /srv/app \
    && chmod 0555 /srv/app/docker/entrypoint.sh \
    && mkdir -p /srv/app/staticfiles /data/media /tmp/app \
    && DJANGO_DEBUG=1 python manage.py collectstatic --noinput --verbosity 0 \
    && chown -R 10001:10001 /srv/app/staticfiles /data/media /tmp/app
USER 10001:10001
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=6 CMD python -c "import urllib.request; request=urllib.request.Request('http://127.0.0.1:8000/health/',headers={'Host':'localhost'}); raise SystemExit(0 if urllib.request.urlopen(request,timeout=2).status==200 else 1)"
ENTRYPOINT ["/srv/app/docker/entrypoint.sh"]
