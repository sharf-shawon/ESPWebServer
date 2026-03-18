"""Redis cache service for build artifacts and job state."""
from __future__ import annotations

import json
from typing import Any

import structlog

from app.core.config import settings

log = structlog.get_logger()

try:
    import redis.asyncio as aioredis
    _redis_available = True
except ImportError:
    _redis_available = False


class CacheService:
    """Thin wrapper around Redis for job state and firmware caching."""

    def __init__(self) -> None:
        self._client: Any = None

    async def _get_client(self) -> Any:
        if self._client is None and _redis_available:
            try:
                client = aioredis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=1,
                )
                # Verify connectivity eagerly so failures fall back to in-memory
                await client.ping()
                self._client = client
            except Exception as exc:
                log.warning("redis_unavailable", error=str(exc))
        return self._client

    async def set_job_status(
        self,
        job_id: str,
        status: str,
        *,
        firmware_key: str = "",
        firmware_size: int = 0,
        error: str = "",
    ) -> None:
        client = await self._get_client()
        data: dict[str, Any] = {
            "status": status,
            "firmware_key": firmware_key,
            "firmware_size": firmware_size,
            "error": error,
        }
        key = f"job:{job_id}"
        if client:
            await client.set(key, json.dumps(data), ex=settings.cache_ttl)
        else:
            # In-memory fallback for dev without Redis
            _mem_store[key] = data

    async def get_job_status(self, job_id: str) -> dict[str, Any] | None:
        client = await self._get_client()
        key = f"job:{job_id}"
        if client:
            raw = await client.get(key)
            if raw:
                return json.loads(raw)  # type: ignore[no-any-return]
            return None
        return _mem_store.get(key)  # type: ignore[return-value]

    async def append_job_log(self, job_id: str, message: str) -> None:
        client = await self._get_client()
        key = f"log:{job_id}"
        if client:
            await client.rpush(key, message)
            await client.expire(key, settings.cache_ttl)
        else:
            if key not in _mem_store:
                _mem_store[key] = []
            _mem_store[key].append(message)  # type: ignore[union-attr]

    async def get_job_logs(self, job_id: str, start: int = 0) -> list[str]:
        client = await self._get_client()
        key = f"log:{job_id}"
        if client:
            items = await client.lrange(key, start, -1)
            return list(items)
        stored = _mem_store.get(key, [])
        return list(stored[start:])  # type: ignore[index]

    async def set_firmware_cache(self, content_hash: str, firmware_key: str) -> None:
        client = await self._get_client()
        key = f"fw:{content_hash}"
        if client:
            await client.set(key, firmware_key, ex=settings.cache_ttl)
        else:
            _mem_store[key] = firmware_key

    async def get_firmware_key(self, content_hash: str) -> str | None:
        client = await self._get_client()
        key = f"fw:{content_hash}"
        if client:
            return await client.get(key)  # type: ignore[no-any-return]
        return _mem_store.get(key)  # type: ignore[return-value]


# Simple in-memory fallback when Redis is unavailable (development only)
_mem_store: dict[str, Any] = {}
