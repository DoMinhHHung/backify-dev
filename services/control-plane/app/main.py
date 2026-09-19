from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.adapter.postgres.connection import Database
from app.config import get_settings

logger = structlog.get_logger()


def configure_logging() -> None:
    settings = get_settings()
    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    if settings.log_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog.stdlib, settings.log_level.upper(), 20)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    settings = get_settings()
    logger.info("app_starting", env=settings.app_env, host=settings.app_host, port=settings.app_port)
    db = Database(settings)
    try:
        await db.connect()
        app.state.db = db
        logger.info("db_connected")
    except Exception as exc:
        logger.error("db_connect_failed", error=str(exc))
        app.state.db = None
    yield
    if getattr(app.state, "db", None) is not None:
        await app.state.db.disconnect()
    logger.info("app_stopped")


app = FastAPI(title="Backify Control Plane", lifespan=lifespan)


@app.get("/health")
async def health() -> JSONResponse:
    db_status = "error"
    db: Database | None = getattr(app.state, "db", None)
    if db is not None:
        ok = await db.health_check()
        db_status = "ok" if ok else "error"
    status = "ok" if db_status == "ok" else "degraded"
    return JSONResponse(
        status_code=200 if db_status == "ok" else 503,
        content={"status": status, "db": db_status},
    )