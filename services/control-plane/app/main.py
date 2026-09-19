from contextlib import asynccontextmanager
from typing import AsyncIterator

import asyncpg
import structlog
from fastapi import FastAPI
from fastapi.responses import JSONResponse

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
    app.state.db_pool = None
    try:
        app.state.db_pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=settings.database_pool_min_size,
            max_size=settings.database_pool_max_size,
        )
        async with app.state.db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        logger.info("db_connected")
    except Exception as exc:
        logger.error("db_connect_failed", error=str(exc))
        app.state.db_pool = None
    yield
    if app.state.db_pool is not None:
        await app.state.db_pool.close()
        logger.info("db_pool_closed")
    logger.info("app_stopped")


app = FastAPI(title="Backify Control Plane", lifespan=lifespan)


@app.get("/health")
async def health() -> JSONResponse:
    db_status = "error"
    pool = getattr(app.state, "db_pool", None)
    if pool is not None:
        try:
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            db_status = "ok"
        except Exception:
            db_status = "error"
    status = "ok" if db_status == "ok" else "degraded"
    return JSONResponse(
        status_code=200 if db_status == "ok" else 503,
        content={"status": status, "db": db_status},
    )