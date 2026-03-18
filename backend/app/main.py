"""FastAPI application entry point."""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api import build, firmware, health
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()
log = structlog.get_logger()

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    log.info("starting", version="1.0.0", env=settings.environment)
    yield
    log.info("shutdown")


app = FastAPI(
    title="ESP Web Deployer",
    description="Compile and flash ESP8266/ESP32 firmware from HTML/CSS/JS",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(build.router, prefix="/api", tags=["build"])
app.include_router(firmware.router, prefix="/api", tags=["firmware"])

# WebSocket routes
from app.api import ws  # noqa: E402
app.include_router(ws.router, prefix="/ws", tags=["websocket"])

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_config=None,
    )
