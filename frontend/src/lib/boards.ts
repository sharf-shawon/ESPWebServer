export interface BoardPin {
  led?: number;
  tx?: number;
  rx?: number;
}

export interface Board {
  id: string;
  name: string;
  chip: "esp8266" | "esp32";
  flashSize: string;
  spiffsSize: string;
  platformioEnv: string;
  pins: BoardPin;
  description: string;
}

export const BOARDS: Board[] = [
  {
    id: "nodemcu",
    name: "NodeMCU v2 (ESP8266)",
    chip: "esp8266",
    flashSize: "4MB",
    spiffsSize: "3MB",
    platformioEnv: "nodemcuv2",
    pins: { led: 2, tx: 1, rx: 3 },
    description: "Popular ESP8266 dev board with USB-Serial",
  },
  {
    id: "wemos-d1-mini",
    name: "Wemos D1 Mini (ESP8266)",
    chip: "esp8266",
    flashSize: "4MB",
    spiffsSize: "3MB",
    platformioEnv: "d1_mini",
    pins: { led: 2, tx: 1, rx: 3 },
    description: "Compact ESP8266 board, ideal for projects",
  },
  {
    id: "esp32-devkit",
    name: "ESP32-DevKit v1",
    chip: "esp32",
    flashSize: "4MB",
    spiffsSize: "1.5MB",
    platformioEnv: "esp32dev",
    pins: { led: 2, tx: 1, rx: 3 },
    description: "Standard ESP32 development board",
  },
  {
    id: "esp32-s2",
    name: "ESP32-S2 DevKit",
    chip: "esp32",
    flashSize: "4MB",
    spiffsSize: "1.5MB",
    platformioEnv: "esp32-s2-saola-1",
    pins: { led: 15, tx: 43, rx: 44 },
    description: "ESP32-S2 with native USB",
  },
  {
    id: "esp32-c3",
    name: "ESP32-C3 DevKit",
    chip: "esp32",
    flashSize: "4MB",
    spiffsSize: "1.5MB",
    platformioEnv: "esp32-c3-devkitm-1",
    pins: { led: 8, tx: 21, rx: 20 },
    description: "ESP32-C3 RISC-V with WiFi+BT",
  },
  {
    id: "lolin-d32",
    name: "LOLIN D32 (ESP32)",
    chip: "esp32",
    flashSize: "4MB",
    spiffsSize: "1.5MB",
    platformioEnv: "lolin_d32",
    pins: { led: 5, tx: 1, rx: 3 },
    description: "ESP32 with LiPo charger",
  },
  {
    id: "feather-esp32",
    name: "Adafruit Feather ESP32",
    chip: "esp32",
    flashSize: "4MB",
    spiffsSize: "1.5MB",
    platformioEnv: "featheresp32",
    pins: { led: 13, tx: 1, rx: 3 },
    description: "Adafruit Feather ESP32 with LiPo",
  },
  {
    id: "az-delivery-esp32",
    name: "AZ-Delivery ESP32 DevKit",
    chip: "esp32",
    flashSize: "4MB",
    spiffsSize: "1.5MB",
    platformioEnv: "az-delivery-devkit-v4",
    pins: { led: 2, tx: 1, rx: 3 },
    description: "AZ-Delivery 38-pin ESP32",
  },
  {
    id: "generic-esp8266",
    name: "Generic ESP8266",
    chip: "esp8266",
    flashSize: "1MB",
    spiffsSize: "512KB",
    platformioEnv: "esp01_1m",
    pins: { led: 2 },
    description: "Generic ESP-01/ESP-12 modules",
  },
  {
    id: "huzzah-esp8266",
    name: "Adafruit HUZZAH ESP8266",
    chip: "esp8266",
    flashSize: "4MB",
    spiffsSize: "3MB",
    platformioEnv: "huzzah",
    pins: { led: 0, tx: 1, rx: 3 },
    description: "Adafruit HUZZAH with ESP8266",
  },
];
