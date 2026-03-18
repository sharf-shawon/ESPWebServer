"""Build endpoint: submit HTML/CSS/JS for firmware compilation."""
from __future__ import annotations

import hashlib
import json
import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.services.builder import BuildService
from app.services.cache import CacheService

log = structlog.get_logger()
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class BuildRequest(BaseModel):
    board_id: str = Field(..., pattern=r"^[a-z0-9_-]{3,40}$")
    html: str = Field(default="", max_length=786432)
    css: str = Field(default="", max_length=131072)
    js: str = Field(default="", max_length=131072)

    @field_validator("board_id")
    @classmethod
    def validate_board(cls, v: str) -> str:
        valid_boards = {
            "nodemcu", "wemos-d1-mini", "esp32-devkit", "esp32-s2",
            "esp32-c3", "lolin-d32", "feather-esp32", "az-delivery-esp32",
            "generic-esp8266", "huzzah-esp8266",
        }
        if v not in valid_boards:
            raise ValueError(f"Unknown board: {v}")
        return v


class BuildResponse(BaseModel):
    job_id: str
    cached: bool
    estimated_seconds: int


def _content_hash(req: BuildRequest) -> str:
    payload = json.dumps(
        {"board": req.board_id, "html": req.html, "css": req.css, "js": req.js},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


@router.post("/build", response_model=BuildResponse)
@limiter.limit(settings.rate_limit_builds)
async def start_build(
    request: Request,
    build_req: BuildRequest,
    background_tasks: BackgroundTasks,
) -> BuildResponse:
    total_size = len(build_req.html) + len(build_req.css) + len(build_req.js)
    if total_size > settings.max_html_size:
        raise HTTPException(
            status_code=413,
            detail=f"Content too large: {total_size} bytes (max {settings.max_html_size})",
        )

    content_hash = _content_hash(build_req)
    job_id = str(uuid.uuid4())

    log.info("build_requested", board=build_req.board_id, hash=content_hash, job_id=job_id)

    cache = CacheService()
    cached_key = await cache.get_firmware_key(content_hash)
    if cached_key:
        log.info("cache_hit", hash=content_hash, job_id=job_id)
        await cache.set_job_status(job_id, "cached", firmware_key=cached_key)
        return BuildResponse(job_id=job_id, cached=True, estimated_seconds=0)

    await cache.set_job_status(job_id, "queued")
    builder = BuildService(cache)
    background_tasks.add_task(
        builder.build,
        job_id, build_req.board_id, build_req.html, build_req.css, build_req.js, content_hash,
    )

    return BuildResponse(job_id=job_id, cached=False, estimated_seconds=60)
