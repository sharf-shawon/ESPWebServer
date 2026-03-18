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

  Serial.println("LittleFS mounted OK");

  wifiManager.setConfigPortalSSID("esp-web-server");
  wifiManager.setConfigPortalTimeout(180);

  if (!wifiManager.autoConnect("esp-web-server")) {
    Serial.println("WiFi config timeout, restarting");
    ESP.restart();
  }

  Serial.println("Connected! IP: " + WiFi.localIP().toString());

  server.serveStatic("/", LittleFS, "/").setDefaultFile("index.html");

  server.on("/led/toggle", HTTP_GET, [](AsyncWebServerRequest *request) {
    static bool ledState = false;
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState ? LOW : HIGH);
    request->send(200, "text/plain", ledState ? "ON" : "OFF");
  });

  server.on("/api/info", HTTP_GET, [](AsyncWebServerRequest *request) {
    String json = "{\"ip\":\"" + WiFi.localIP().toString() +
                  "\",\"ssid\":\"" + WiFi.SSID() +
                  "\",\"rssi\":" + String(WiFi.RSSI()) +
                  ",\"chip\":\"ESP32\",\"heap\":" + String(ESP.getFreeHeap()) + "}";
    request->send(200, "application/json", json);
  });

  server.onNotFound([](AsyncWebServerRequest *request) {
    request->send(404, "text/plain", "Not found");
  });

  server.begin();
  ledPulse(2, 100, 100);
  Serial.println("HTTP server started on port 80");
}

void loop() {
  delay(10);
}
