# ESP Web Deployer 🚀

Flash single-page websites to **ESP8266/ESP32** boards from your browser in 5 minutes.

[![CI](https://github.com/sharf-shawon/ESPWebServer/actions/workflows/ci.yml/badge.svg)](https://github.com/sharf-shawon/ESPWebServer/actions/workflows/ci.yml)
[![Docker](https://github.com/sharf-shawon/ESPWebServer/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/sharf-shawon/ESPWebServer/actions/workflows/docker-publish.yml)

## What It Does

1. **Paste** your HTML/CSS/JS into the browser editor
2. **Select** your ESP board (NodeMCU, ESP32-DevKit, etc.)
3. **Build** — backend compiles firmware with PlatformIO (60s, cached)
4. **Flash** — browser flashes via Web Serial API (no drivers needed!)
5. **Connect** to your ESP's WiFi AP → configure your home WiFi → done!

## Quick Start (Docker)

```bash
# Pull and run
docker pull ghcr.io/sharf-shawon/espwebserver:latest
docker run -p 80:80 ghcr.io/sharf-shawon/espwebserver:latest

# Open http://localhost
```

### With Redis cache (recommended for production):

```bash
git clone https://github.com/sharf-shawon/ESPWebServer.git
cd ESPWebServer
docker compose -f docker/docker-compose.prod.yml up
```

## Requirements

- **Browser**: Chrome 89+ or Edge 89+ (Web Serial API)
- **Connection**: HTTPS or localhost
- **Board**: ESP8266 or ESP32 with USB-Serial chip (CH340, CP210x, FTDI)

## Supported Boards (10+)

| Board | Chip | Flash |
|-------|------|-------|
| NodeMCU v2 | ESP8266 | 4MB |
| Wemos D1 Mini | ESP8266 | 4MB |
| ESP32-DevKit v1 | ESP32 | 4MB |
| ESP32-S2 DevKit | ESP32-S2 | 4MB |
| ESP32-C3 DevKit | ESP32-C3 | 4MB |
| LOLIN D32 | ESP32 | 4MB |
| Adafruit HUZZAH | ESP8266 | 4MB |
| Adafruit Feather ESP32 | ESP32 | 4MB |
| AZ-Delivery ESP32 | ESP32 | 4MB |
| Generic ESP8266 | ESP8266 | 1MB |

See [docs/board-support.md](docs/board-support.md) for full details.

## Architecture

```
Browser (React + shadcn/ui)
  ├── HTML/CSS/JS editor + live preview
  ├── Board selector (10+ presets)
  ├── esptool-js Web Serial flashing
  └── WebSocket build progress

FastAPI Backend
  ├── PlatformIO compilation (sandboxed)
  ├── Redis binary cache (80%+ hit rate)
  └── Rate limiting (5 builds/min)

ESP Firmware
  ├── WiFiManager captive portal
  ├── LittleFS (stores your HTML/CSS/JS)
  ├── ESPAsyncWebServer
  └── LED feedback + OTA endpoint
```

## Development Setup

### Backend
```bash
cd backend
pip install uv
uv pip install --system fastapi uvicorn[standard] redis pydantic pydantic-settings \
  websockets python-multipart aiofiles httpx structlog slowapi python-dotenv
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Tests
```bash
cd backend && pytest tests/ -v
cd frontend && npm run build
```

## After Flashing

1. Board creates WiFi AP: **`esp-web-server`**
2. Connect your phone/laptop to that AP
3. Open **`192.168.4.1`** in your browser
4. Enter your home WiFi credentials
5. Board connects and displays its local IP
6. Open that IP to see your website! 🎉

## Security

- HTTPS required for Web Serial (use reverse proxy in production)
- Content Security Policy headers on all responses
- Rate limiting (5 builds/minute per IP)
- Board ID validated against allowlist
- HTML sanitized before preview (DOMPurify)
- See [SECURITY.md](SECURITY.md) for vulnerability reporting

## License

MIT — see [LICENSE](LICENSE)

## Contributing

PRs welcome! See [copilot-instructions.md](copilot-instructions.md) for conventions.
