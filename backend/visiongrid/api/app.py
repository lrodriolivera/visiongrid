from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from visiongrid.api.routes import cameras, detection, events, health, stream
from visiongrid.core.config import Settings, load_config
from visiongrid.api.state import AppState

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    state = app.state.vg
    logger.info("Starting VisionGrid...")

    await state.start()
    logger.info("VisionGrid started — %d cameras configured", len(state.settings.cameras))

    yield

    logger.info("Shutting down VisionGrid...")
    await state.stop()


def create_app(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        import os
        config_path = os.environ.get("VISIONGRID_CONFIG_PATH")
        from pathlib import Path
        settings = load_config(Path(config_path) if config_path else None)

    app = FastAPI(
        title="VisionGrid",
        description="Open-source real-time computer vision platform",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.vg = AppState(settings)

    app.include_router(health.router, tags=["Health"])
    app.include_router(cameras.router, prefix="/api/v1", tags=["Cameras"])
    app.include_router(detection.router, prefix="/api/v1", tags=["Detection"])
    app.include_router(events.router, prefix="/api/v1", tags=["Events"])
    app.include_router(stream.router, prefix="/api/v1", tags=["Stream"])

    return app
