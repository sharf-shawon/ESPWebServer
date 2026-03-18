#!/bin/sh
set -e

echo "Starting ESP Web Deployer..."

# Start nginx in background
nginx -g "daemon off;" &
NGINX_PID=$!

# Start FastAPI backend
uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers "${BUILD_WORKERS:-2}" \
    --log-config /dev/null &
UVICORN_PID=$!

# Wait for either process to exit
wait -n $NGINX_PID $UVICORN_PID
EXIT_CODE=$?

echo "A process exited with code $EXIT_CODE, shutting down..."
kill $NGINX_PID $UVICORN_PID 2>/dev/null || true
exit $EXIT_CODE
