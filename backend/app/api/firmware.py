"""Firmware download endpoint."""
from __future__ import annotations

import os
from pathlib import Path

import structlog
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.config import settings
from app.services.cache import CacheService

log = structlog.get_logger()
router = APIRouter()


@router.get("/firmware/{job_id}/download")
async def download_firmware(job_id: str) -> FileResponse:
    """Download compiled firmware binary."""
    cache = CacheService()
    job = await cache.get_job_status(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    status = job.get("status")
    if status not in ("success", "cached"):
        raise HTTPException(status_code=400, detail=f"Firmware not ready: {status}")

    firmware_key = job.get("firmware_key", "")
    firmware_path = Path(settings.firmware_dir) / firmware_key

    if not firmware_path.exists():
        raise HTTPException(status_code=404, detail="Firmware file not found")

    return FileResponse(
        path=str(firmware_path),
        media_type="application/octet-stream",
        filename=f"firmware-{job_id[:8]}.bin",
        headers={
            "Content-Disposition": f'attachment; filename="firmware-{job_id[:8]}.bin"',
            "X-Job-Id": job_id,
        },
    )
