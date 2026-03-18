"""WebSocket endpoint for build progress."""
from __future__ import annotations

import asyncio
import json

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.cache import CacheService

log = structlog.get_logger()
router = APIRouter()


@router.websocket("/build/{job_id}")
async def build_progress(websocket: WebSocket, job_id: str) -> None:
    await websocket.accept()
    log.info("ws_connected", job_id=job_id)

    cache = CacheService()
    timeout = 130  # slightly more than build timeout
    poll_interval = 0.5
    elapsed = 0.0

    try:
        # Stream log messages from Redis list
        last_index = 0
        while elapsed < timeout:
            job = await cache.get_job_status(job_id)
            if not job:
                await websocket.send_text(
                    json.dumps({"type": "error", "message": "Job not found"})
                )
                break

            # Send any new log lines
            logs = await cache.get_job_logs(job_id, start=last_index)
            for entry in logs:
                await websocket.send_text(entry)
                last_index += 1

            status = job.get("status")

            if status == "success":
                firmware_key = job.get("firmware_key", "")
                size = job.get("firmware_size", 0)
                await websocket.send_text(
                    json.dumps({
                        "type": "success",
                        "message": "Build complete!",
                        "progress": 100,
                        "downloadUrl": f"/api/firmware/{job_id}/download",
                        "firmwareSize": size,
                    })
                )
                break

            elif status == "cached":
                firmware_key = job.get("firmware_key", "")
                await websocket.send_text(
                    json.dumps({
                        "type": "success",
                        "message": "Using cached firmware!",
                        "progress": 100,
                        "downloadUrl": f"/api/firmware/{job_id}/download",
                    })
                )
                break

            elif status == "error":
                error_msg = job.get("error", "Build failed")
                await websocket.send_text(
                    json.dumps({"type": "error", "message": error_msg})
                )
                break

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        else:
            await websocket.send_text(
                json.dumps({"type": "error", "message": "Build timed out"})
            )

    except WebSocketDisconnect:
        log.info("ws_disconnected", job_id=job_id)
    except Exception as exc:
        log.error("ws_error", job_id=job_id, error=str(exc))
        try:
            await websocket.send_text(
                json.dumps({"type": "error", "message": str(exc)})
            )
        except Exception:
            pass
    finally:
        log.info("ws_closed", job_id=job_id)
