"""PlatformIO project template generator."""
from __future__ import annotations


class TemplateService:
    def get_platformio_ini(self, chip: str, env: str) -> str:
        if chip == "esp8266":
            return self._esp8266_ini(env)
        return self._esp32_ini(env)

    def _esp8266_ini(self, env: str) -> str:
        return f"""[env:{env}]
platform = espressif8266
board = {env}
framework = arduino
monitor_speed = 115200
board_build.filesystem = littlefs
lib_deps =
    tzapu/WiFiManager@^0.16.0
    me-no-dev/ESPAsyncTCP@^1.2.2
    me-no-dev/ESP Async WebServer@^1.2.3
build_flags =
    -D BOARD_ESP8266
    -D CONFIG_LITTLEFS_SPIFFS_COMPAT=1
"""

    def _esp32_ini(self, env: str) -> str:
        return f"""[env:{env}]
platform = espressif32
board = {env}
framework = arduino
monitor_speed = 115200
board_build.filesystem = littlefs
lib_deps =
    tzapu/WiFiManager@^2.0.17
    esphome/ESPAsyncWebServer-esphome@^3.2.2
    esphome/AsyncTCP-esphome@^2.1.4
build_flags =
    -D BOARD_ESP32
"""

    def get_main_cpp(self, chip: str) -> str:
        if chip == "esp8266":
            return _ESP8266_MAIN
        return _ESP32_MAIN


_ESP8266_MAIN = r"""
#include <Arduino.h>
#include <LittleFS.h>
#include <WiFiManager.h>
#include <ESPAsyncWebServer.h>

#define LED_PIN 2

AsyncWebServer server(80);
WiFiManager wifiManager;

void ledPulse(int count, int onMs, int offMs) {
  for (int i = 0; i < count; i++) {
    digitalWrite(LED_PIN, LOW);
    delay(onMs);
    digitalWrite(LED_PIN, HIGH);
    delay(offMs);
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);

  if (!LittleFS.begin()) {
    Serial.println("LittleFS mount failed");
    ledPulse(5, 500, 200); // long pulse = error
    return;
  }

  wifiManager.setConfigPortalSSID("esp-web-server");
  wifiManager.setConfigPortalTimeout(180);
  if (!wifiManager.autoConnect("esp-web-server")) {
    Serial.println("WiFi config timeout, restarting");
    ESP.restart();
  }

  Serial.println("WiFi connected: " + WiFi.localIP().toString());

  server.serveStatic("/", LittleFS, "/").setDefaultFile("index.html");

  server.on("/led/toggle", HTTP_GET, [](AsyncWebServerRequest *request) {
    static bool state = false;
    state = !state;
    digitalWrite(LED_PIN, state ? LOW : HIGH);
    request->send(200, "text/plain", state ? "ON" : "OFF");
  });

  server.on("/api/info", HTTP_GET, [](AsyncWebServerRequest *request) {
    String json = "{\"ip\":\"" + WiFi.localIP().toString() +
                  "\",\"ssid\":\"" + WiFi.SSID() +
                  "\",\"rssi\":" + String(WiFi.RSSI()) +
                  ",\"chip\":\"ESP8266\"}";
    request->send(200, "application/json", json);
  });

  server.onNotFound([](AsyncWebServerRequest *request) {
    request->send(404, "text/plain", "Not found");
  });

  server.begin();
  ledPulse(2, 100, 100); // short pulse = success
  Serial.println("Web server started");
}

void loop() {
  // Blink LED briefly on request (handled in server callbacks)
  delay(10);
}
"""

_ESP32_MAIN = r"""
#include <Arduino.h>
#include <LittleFS.h>
#include <WiFiManager.h>
#include <ESPAsyncWebServer.h>

#define LED_PIN 2

AsyncWebServer server(80);
WiFiManager wifiManager;

void ledPulse(int count, int onMs, int offMs) {
  for (int i = 0; i < count; i++) {
    digitalWrite(LED_PIN, LOW);
    delay(onMs);
    digitalWrite(LED_PIN, HIGH);
    delay(offMs);
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);

  if (!LittleFS.begin(true)) {
    Serial.println("LittleFS mount failed");
    ledPulse(5, 500, 200);
    return;
  }

  wifiManager.setConfigPortalSSID("esp-web-server");
  wifiManager.setConfigPortalTimeout(180);
  if (!wifiManager.autoConnect("esp-web-server")) {
    Serial.println("WiFi config timeout, restarting");
    ESP.restart();
  }

  Serial.println("WiFi connected: " + WiFi.localIP().toString());

  server.serveStatic("/", LittleFS, "/").setDefaultFile("index.html");

  server.on("/led/toggle", HTTP_GET, [](AsyncWebServerRequest *request) {
    static bool state = false;
    state = !state;
    digitalWrite(LED_PIN, state ? LOW : HIGH);
    request->send(200, "text/plain", state ? "ON" : "OFF");
  });

  server.on("/api/info", HTTP_GET, [](AsyncWebServerRequest *request) {
    String json = "{\"ip\":\"" + WiFi.localIP().toString() +
                  "\",\"ssid\":\"" + WiFi.SSID() +
                  "\",\"rssi\":" + String(WiFi.RSSI()) +
                  ",\"chip\":\"ESP32\"}";
    request->send(200, "application/json", json);
  });

  server.onNotFound([](AsyncWebServerRequest *request) {
    request->send(404, "text/plain", "Not found");
  });

  server.begin();
  ledPulse(2, 100, 100);
  Serial.println("Web server started");
}

void loop() {
  delay(10);
}
"""
