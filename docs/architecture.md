# Architecture

## Overview

ESP Web Deployer is a three-tier application:

```
Browser (React + esptool-js)
    │
    ├── HTTP/WS → Nginx (port 80)
    │               │
    │               ├── /api/* → FastAPI (port 8000)
    │               └── /ws/*  → FastAPI WebSocket
    │
FastAPI Backend
    ├── Build API (POST /api/build)
    ├── WebSocket (WS /ws/build/{job_id})
    ├── Download (GET /api/firmware/{job_id}/download)
    └── PlatformIO (sandboxed subprocess)
            │
            └── Redis (job state + firmware cache)
```

## Data Flow

1. **User** pastes HTML/CSS/JS and selects board
2. **Frontend** sends POST `/api/build` with content + board ID
3. **Backend** checks Redis cache by SHA-256 hash of content
4. If cache miss: spawns PlatformIO build as background task
5. **WebSocket** streams build logs in real-time to browser
6. On success: firmware `.bin` stored in `/tmp/firmware/`
7. **Frontend** downloads binary via GET `/api/firmware/{id}/download`
8. **esptool-js** uses Web Serial API to erase+write+verify ESP flash

## Components

### Frontend (`frontend/`)
- **React 18** + **Vite 5** (HMR dev, optimized prod build)
- **shadcn/ui** + **Tailwind CSS** for UI
- **esptool-js** (Espressif official) for Web Serial flashing
- **DOMPurify** for preview sanitization

### Backend (`backend/`)
- **FastAPI 0.115+** async web framework
- **Redis 7** for job state, build logs, and binary cache
- **PlatformIO Core 6.1** for ESP firmware compilation
- **slowapi** for rate limiting (5 builds/min per IP)
- **structlog** for structured JSON logging

### Firmware (`firmware/`)
- **ESPAsyncWebServer** for non-blocking HTTP
- **WiFiManager** for captive portal WiFi setup
- **LittleFS** for storing HTML/CSS/JS files
- LED feedback: 2 short = success, 5 long = error

## Security

- Board ID validated against explicit allowlist
- Content size limited to 512KB server-side
- Rate limiting via Redis (5 builds/minute)
- Content Security Policy headers via nginx
- DOMPurify sanitization in live preview
- HTTPS required for Web Serial API
