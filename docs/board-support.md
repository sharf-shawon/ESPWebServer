# Board Support

## Supported Boards

| Board | Chip | Flash | SPIFFS | PlatformIO Env |
|-------|------|-------|--------|----------------|
| NodeMCU v2 | ESP8266 | 4MB | 3MB | `nodemcuv2` |
| Wemos D1 Mini | ESP8266 | 4MB | 3MB | `d1_mini` |
| Adafruit HUZZAH | ESP8266 | 4MB | 3MB | `huzzah` |
| Generic ESP8266 | ESP8266 | 1MB | 512KB | `esp01_1m` |
| ESP32-DevKit v1 | ESP32 | 4MB | 1.5MB | `esp32dev` |
| ESP32-S2 DevKit | ESP32-S2 | 4MB | 1.5MB | `esp32-s2-saola-1` |
| ESP32-C3 DevKit | ESP32-C3 | 4MB | 1.5MB | `esp32-c3-devkitm-1` |
| LOLIN D32 | ESP32 | 4MB | 1.5MB | `lolin_d32` |
| Adafruit Feather ESP32 | ESP32 | 4MB | 1.5MB | `featheresp32` |
| AZ-Delivery ESP32 | ESP32 | 4MB | 1.5MB | `az-delivery-devkit-v4` |

## Adding a New Board

1. Add board to `frontend/src/lib/boards.ts`
2. Add mapping to `backend/app/services/builder.py` (`BOARD_ENV_MAP`, `BOARD_CHIP_MAP`)
3. Add board validation in `backend/app/api/build.py`
4. Add firmware template in `firmware/templates/`
5. Add CI test in `.github/workflows/firmware-test.yml`
6. Open a PR with board documentation

## LED Feedback

| Pattern | Meaning |
|---------|---------|
| 2x short blink | Boot success, server running |
| 5x long blink | Error (LittleFS, WiFi, etc.) |
| Solid on | Processing request |
