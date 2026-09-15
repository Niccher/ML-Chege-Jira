"""FastAPI application entrypoint and lifespan definition."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import v1_router
from app.config import settings
from app.db.schema_guard import ensure_ai_tables_exist
from app.db.session import engine

# Setup root logging
logging.basicConfig(
    level=logging.INFO if settings.APP_ENV != "development" else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ml_chege_jira")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifespan context manager."""
    logger.info("Starting ML Chege Jira service (env=%s)...", settings.APP_ENV)

    # 1. Fallback verification that ai_* tables exist in MySQL
    await ensure_ai_tables_exist(engine)

    logger.info(
        "ML backend initialized. Default model: '%s', compute mode: %s",
        settings.DEFAULT_MODEL,
        "GPU" if settings.N_GPU_LAYERS != 0 else "CPU",
    )

    yield

    logger.info("Shutting down ML Chege Jira service...")
    await engine.dispose()
    logger.info("Database connection pool closed.")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="ML Chege Jira API",
        description="High-performance LLM REST backend for Chege Jira WebApp powered by llama-cpp-python",
        version="0.1.0",
        docs_url="/docs" if settings.APP_ENV == "development" else None,
        redoc_url="/redoc" if settings.APP_ENV == "development" else None,
        openapi_url="/openapi.json" if settings.APP_ENV == "development" else None,
        lifespan=lifespan,
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount v1 Master Router
    app.include_router(v1_router)

    # Validation Error Handler
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": "validation_error",
                    "message": "Invalid request payload or query parameter",
                    "details": exc.errors(),
                },
            },
        )

    return app


app = create_app()
