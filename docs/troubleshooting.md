# Troubleshooting

## Web Serial Issues

**"Web Serial API not supported"**
- Use Chrome 89+ or Edge 89+
- Requires HTTPS or `localhost`
- Cannot be used in Firefox or Safari

**"Failed to open port"**
- Ensure another app (Arduino IDE, etc.) is not using the port
- On Linux, add user to `dialout` group: `sudo usermod -a -G dialout $USER`
- On macOS, check `ls /dev/cu.*` for the port

**Board not connecting during flash**
- Hold **BOOT** button when "Connecting..." appears
- For CH340 chips, install drivers: https://www.wch-ic.com/products/CH340.html
- Try lower baud rate (115200 instead of 921600)

## Build Issues

**"Build timed out"**
- First build downloads toolchains (~200MB), takes 5-10 minutes
- Subsequent builds use cache, typically 30-60s
- Increase `BUILD_TIMEOUT` environment variable

**"PlatformIO not found"**
- Ensure Docker container is running: `docker ps`
- Check logs: `docker logs esp-web-deployer`

**"LittleFS mount failed" on board**
- Flash the SPIFFS image separately:
  ```
  pio run -t uploadfs -e nodemcuv2
  ```
- The web deployer flashes firmware only; SPIFFS upload requires PlatformIO

**ESP8266 crash: `Exception (9)` with `excvaddr=0x00000003`**
- This usually indicates an invalid/null pointer access in request handling.
- Rebuild and reflash with the latest template firmware (includes safer `/save` parameter handling).
- If you still see resets, erase flash before reflash:
  ```
  pio run -t erase -e nodemcuv2
  pio run -t upload -e nodemcuv2
  pio run -t uploadfs -e nodemcuv2
  ```
- Check serial monitor at `115200` and confirm the board reaches `HTTP server started on port 80`.

## Docker Issues

**Image too large**
- First build includes PlatformIO toolchains (~500MB)
- Run `docker image prune` to remove old layers
- Use the multi-stage build (default Dockerfile)

**Redis connection refused**
- Backend falls back to in-memory store for development
- For production, ensure Redis container is healthy: `docker compose ps`
