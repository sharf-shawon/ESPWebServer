"""PlatformIO firmware builder service."""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import tempfile
from pathlib import Path

import structlog

from app.core.config import settings
from app.services.cache import CacheService
from app.services.template import TemplateService

log = structlog.get_logger()

BOARD_ENV_MAP: dict[str, str] = {
    "nodemcu": "nodemcuv2",
    "wemos-d1-mini": "d1_mini",
    "esp32-devkit": "esp32dev",
    "esp32-s2": "esp32-s2-saola-1",
    "esp32-c3": "esp32-c3-devkitm-1",
    "lolin-d32": "lolin_d32",
    "feather-esp32": "featheresp32",
    "az-delivery-esp32": "az-delivery-devkit-v4",
    "generic-esp8266": "esp01_1m",
    "huzzah-esp8266": "huzzah",
}

BOARD_CHIP_MAP: dict[str, str] = {
    "nodemcu": "esp8266",
    "wemos-d1-mini": "esp8266",
    "generic-esp8266": "esp8266",
    "huzzah-esp8266": "esp8266",
    "esp32-devkit": "esp32",
    "esp32-s2": "esp32",
    "esp32-c3": "esp32",
    "lolin-d32": "esp32",
    "feather-esp32": "esp32",
    "az-delivery-esp32": "esp32",
}


class BuildService:
    def __init__(self, cache: CacheService) -> None:
        self._cache = cache
        self._template = TemplateService()

    async def build(
        self,
        job_id: str,
        board_id: str,
        html: str,
        css: str,
        js: str,
        content_hash: str,
    ) -> None:
        """Run PlatformIO build in a temp directory, cache result."""
        await self._cache.set_job_status(job_id, "building")
        await self._log(job_id, "progress", "Setting up build environment...", 5)

        try:
            chip = BOARD_CHIP_MAP.get(board_id, "esp8266")
            env = BOARD_ENV_MAP.get(board_id, "nodemcuv2")
            with tempfile.TemporaryDirectory(prefix="espbuild_") as tmpdir:
                project_dir = Path(tmpdir)
                await self._prepare_project(project_dir, chip, env, html, css, js)
                await self._log(job_id, "progress", "Compiling firmware (this may take 60-90s)...", 15)
                firmware_bytes = await self._run_platformio(job_id, project_dir, env)
                await self._log(job_id, "progress", "Saving firmware...", 90)
                firmware_key = await self._save_firmware(firmware_bytes, content_hash, board_id)

            await self._cache.set_firmware_cache(content_hash, firmware_key)
            await self._cache.set_job_status(
                job_id, "success",
                firmware_key=firmware_key,
                firmware_size=len(firmware_bytes),
            )
            await self._log(job_id, "success", f"Build successful! Firmware size: {len(firmware_bytes) // 1024} KB", 100)

        except Exception as exc:
            log.error("build_failed", job_id=job_id, error=str(exc))
            await self._cache.set_job_status(job_id, "error", error=str(exc))
            await self._log(job_id, "error", f"Build failed: {exc}")

    async def _prepare_project(
        self,
        project_dir: Path,
        chip: str,
        env: str,
        html: str,
        css: str,
        js: str,
    ) -> None:
        """Write PlatformIO project files."""
        src_dir = project_dir / "src"
        data_dir = project_dir / "data"
        src_dir.mkdir()
        data_dir.mkdir()

        # platformio.ini
        pio_ini = self._template.get_platformio_ini(chip, env)
        (project_dir / "platformio.ini").write_text(pio_ini)

        # main.cpp
        main_cpp = self._template.get_main_cpp(chip)
        (src_dir / "main.cpp").write_text(main_cpp)

        # SPIFFS data files
        (data_dir / "index.html").write_text(html or "<h1>ESP Web Server</h1>")
        (data_dir / "style.css").write_text(css)
        (data_dir / "script.js").write_text(js)

    async def _run_platformio(
        self, job_id: str, project_dir: Path, env: str
    ) -> bytes:
        """Execute PlatformIO build and return firmware bytes."""
        cmd = [
            "pio", "run",
            "-e", env,
            "--project-dir", str(project_dir),
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env={**os.environ, "PLATFORMIO_HOME_DIR": settings.platformio_home},
        )

        assert proc.stdout is not None
        async for line in proc.stdout:
            decoded = line.decode("utf-8", errors="replace").rstrip()
            if decoded:
                await self._log(job_id, "log", decoded)

        try:
            await asyncio.wait_for(proc.wait(), timeout=settings.build_timeout)
        except asyncio.TimeoutError:
            proc.kill()
            raise TimeoutError(f"Build timed out after {settings.build_timeout}s")

        if proc.returncode != 0:
            raise RuntimeError(f"PlatformIO exited with code {proc.returncode}")

        # Find the .bin file
        firmware_file = self._find_firmware(project_dir, env)
        return firmware_file.read_bytes()

    def _find_firmware(self, project_dir: Path, env: str) -> Path:
        """Locate the compiled .bin firmware file."""
        candidates = list(project_dir.glob(f".pio/build/{env}/*.bin"))
        # Filter out SPIFFS/littlefs images
        fw_candidates = [
            f for f in candidates
            if "spiffs" not in f.name.lower() and "littlefs" not in f.name.lower()
        ]
        if not fw_candidates:
            raise FileNotFoundError(f"No firmware .bin found in {project_dir}/.pio/build/{env}/")
        return fw_candidates[0]

    async def _save_firmware(self, data: bytes, content_hash: str, board_id: str) -> str:
        """Save firmware to persistent storage, return the key (filename)."""
        output_dir = Path(settings.firmware_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{board_id}-{content_hash}.bin"
        path = output_dir / filename
        path.write_bytes(data)
        return filename

    async def _log(
        self,
        job_id: str,
        msg_type: str,
        message: str,
        progress: int | None = None,
    ) -> None:
        payload: dict[str, object] = {"type": msg_type, "message": message}
        if progress is not None:
            payload["progress"] = progress
        await self._cache.append_job_log(job_id, json.dumps(payload))
