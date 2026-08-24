from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from . import __version__
from .config import settings
from .database import SessionLocal
from .manifest import ModelManifest
from .registry import PipelineRegistry
from .storage import Storage
from .workflow import resume_jobs

manifest = ModelManifest.load(settings.model_manifest_path)
registry = PipelineRegistry(manifest, settings.model_dir)
storage = Storage(settings.data_dir)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    storage.cleanup_trash()
    resume_jobs(registry, storage)
    yield


app = FastAPI(
    title="Local Vision API",
    version=__version__,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)


@app.get("/v1/health")
def health() -> dict[str, str]:
    database = "ready"
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
    except Exception:
        database = "unavailable"
    try:
        pipeline = registry.get(settings.active_pipeline)
        ready, pipeline_status = pipeline.health_check()
    except (KeyError, FileNotFoundError, ValueError):
        ready, pipeline_status = False, "model_not_installed_or_checksum_invalid"
    overall = "ok" if database == "ready" and ready else "degraded"
    return {"status": overall, "database": database, "pipeline": pipeline_status}


from .api import router  # noqa: E402

app.include_router(router)
