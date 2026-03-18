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
    me-no-dev/ESPAsyncTCP@^1.2.2
    esphome/ESPAsyncWebServer-esphome@^3.2.2
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
#include <ESP8266WiFi.h>
#include <ESPAsyncWebServer.h>

#define LED_PIN 2
#define WIFI_CONFIG_FILE "/wifi.cfg"
#define CONNECT_TIMEOUT_MS 15000

AsyncWebServer server(80);

void ledPulse(int count, int onMs, int offMs) {
  for (int i = 0; i < count; i++) {
    digitalWrite(LED_PIN, LOW);
    delay(onMs);
    digitalWrite(LED_PIN, HIGH);
    delay(offMs);
  }
}

bool readWiFiConfig(String &ssid, String &password) {
  if (!LittleFS.exists(WIFI_CONFIG_FILE)) return false;
  File f = LittleFS.open(WIFI_CONFIG_FILE, "r");
  if (!f) return false;
  ssid = f.readStringUntil('\n');
  password = f.readStringUntil('\n');
  f.close();
  ssid.trim();
  password.trim();
  return ssid.length() > 0;
}

void saveWiFiConfig(const String &ssid, const String &password) {
  File f = LittleFS.open(WIFI_CONFIG_FILE, "w");
  f.println(ssid);
  f.println(password);
  f.close();
}

bool connectToWiFi() {
  String ssid, password;
  if (!readWiFiConfig(ssid, password)) return false;
  Serial.println("Connecting to: " + ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid.c_str(), password.c_str());
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - start > CONNECT_TIMEOUT_MS) return false;
    delay(500);
  }
  return true;
}

void startConfigPortal() {
  Serial.println("Starting config portal AP: esp-web-server");
  WiFi.mode(WIFI_AP);
  WiFi.softAP("esp-web-server");

  server.on("/", HTTP_GET, [](AsyncWebServerRequest *req) {
    req->send(200, "text/html",
      "<!DOCTYPE html><html><head><title>WiFi Setup</title>"
      "<meta name='viewport' content='width=device-width,initial-scale=1'></head>"
      "<body><h2>WiFi Configuration</h2>"
      "<form method='post' action='/save'>"
      "SSID:<br><input name='ssid'><br>"
      "Password:<br><input type='password' name='pass'><br><br>"
      "<button type='submit'>Save &amp; Connect</button>"
      "</form></body></html>");
  });

  server.on("/save", HTTP_POST, [](AsyncWebServerRequest *req) {
    if (!req->hasParam("ssid", true)) {
      req->send(400, "text/plain", "Missing SSID");
      return;
    }
    String ssid = req->getParam("ssid", true)->value();
    String pass = req->hasParam("pass", true)
                    ? req->getParam("pass", true)->value()
                    : "";
    saveWiFiConfig(ssid, pass);
    req->send(200, "text/plain", "Saved! Restarting...");
    delay(500);
    ESP.restart();
  });

  server.onNotFound([](AsyncWebServerRequest *req) {
    req->send(404, "text/plain", "Not found");
  });

  server.begin();
  Serial.println("Config portal running at http://192.168.4.1");
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);

  if (!LittleFS.begin()) {
    Serial.println("LittleFS mount failed - format required?");
    ledPulse(5, 500, 200);
    return;
  }

  if (!connectToWiFi()) {
    startConfigPortal();
    return;
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
  ledPulse(2, 100, 100);
  Serial.println("Web server started");
}

void loop() {
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
