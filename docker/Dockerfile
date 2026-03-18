# syntax=docker/dockerfile:1.7

# =============================================================================
# Stage 1: Frontend build
# =============================================================================
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --prefer-offline

COPY frontend/ ./
RUN npm run build

# =============================================================================
# Stage 2: Python + PlatformIO toolchain builder
# =============================================================================
FROM python:3.13-slim AS backend-builder
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv==0.4.29

# Copy and install Python dependencies
COPY backend/pyproject.toml ./
RUN uv pip install --system --no-cache \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.30.0 \
    websockets>=13.0 \
    redis>=5.1.0 \
    pydantic>=2.9.0 \
    pydantic-settings>=2.5.0 \
    python-multipart>=0.0.12 \
    aiofiles>=24.1.0 \
    httpx>=0.27.0 \
    structlog>=24.4.0 \
    slowapi>=0.1.9 \
    python-dotenv>=1.0.1

# Install PlatformIO
RUN pip install --no-cache-dir platformio==6.1.16

# Pre-install PlatformIO toolchains (bakes toolchains into image for faster builds)
ENV PLATFORMIO_HOME_DIR=/root/.platformio
RUN mkdir -p /tmp/pio-prebuild && \
    echo '[env:nodemcuv2]\nplatform = espressif8266\nboard = nodemcuv2\nframework = arduino' > /tmp/pio-prebuild/platformio.ini && \
    mkdir -p /tmp/pio-prebuild/src && \
    echo 'void setup(){} void loop(){}' > /tmp/pio-prebuild/src/main.cpp && \
    pio run -d /tmp/pio-prebuild -e nodemcuv2 --silent || true

RUN mkdir -p /tmp/pio-prebuild32 && \
    echo '[env:esp32dev]\nplatform = espressif32\nboard = esp32dev\nframework = arduino' > /tmp/pio-prebuild32/platformio.ini && \
    mkdir -p /tmp/pio-prebuild32/src && \
    echo 'void setup(){} void loop(){}' > /tmp/pio-prebuild32/src/main.cpp && \
    pio run -d /tmp/pio-prebuild32 -e esp32dev --silent || true

# =============================================================================
# Stage 3: Runtime image
# =============================================================================
FROM python:3.13-slim AS runtime
WORKDIR /app

# Install nginx and runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=backend-builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin
COPY --from=backend-builder /root/.platformio /root/.platformio

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist /app/static

# Copy backend code
COPY backend/app /app/app

# Copy nginx config
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
RUN rm -f /etc/nginx/sites-enabled/default

# Create firmware output directory
RUN mkdir -p /tmp/firmware /var/log/esp-deployer

# Copy startup script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/api/health || exit 1

ENV PYTHONUNBUFFERED=1
ENV FIRMWARE_DIR=/tmp/firmware
ENV PLATFORMIO_HOME_DIR=/root/.platformio

ENTRYPOINT ["/entrypoint.sh"]
