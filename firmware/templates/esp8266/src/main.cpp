#include <Arduino.h>
#include <LittleFS.h>
#include <ESP8266WiFi.h>
#include <ESPAsyncWebServer.h>
#include <Ticker.h>

#define LED_PIN 2
#define WIFI_CONFIG_FILE "/wifi.cfg"
#define CONNECT_TIMEOUT_MS 15000

AsyncWebServer server(80);
Ticker restartTicker;

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

bool saveWiFiConfig(const String &ssid, const String &password) {
  File f = LittleFS.open(WIFI_CONFIG_FILE, "w");
  if (!f) return false;
  f.println(ssid);
  f.println(password);
  f.close();
  return true;
}

void deferredRestart() {
  ESP.restart();
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
    AsyncWebParameter *ssidParam = req->getParam("ssid", true);
    if (!ssidParam) {
      req->send(400, "text/plain", "Missing SSID parameter");
      return;
    }

    String ssid = ssidParam->value();
    ssid.trim();
    if (ssid.length() == 0) {
      req->send(400, "text/plain", "SSID cannot be empty");
      return;
    }

    AsyncWebParameter *passParam = req->getParam("pass", true);
    String pass = passParam ? passParam->value() : "";

    if (!saveWiFiConfig(ssid, pass)) {
      req->send(500, "text/plain", "Failed to save WiFi config");
      return;
    }

    req->send(200, "text/plain", "Saved! Restarting...");
    restartTicker.once_ms(500, deferredRestart);
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

  Serial.println("LittleFS mounted OK");

  if (!connectToWiFi()) {
    Serial.println("No WiFi credentials or connection failed, entering config mode");
    startConfigPortal();
    return;
  }

  Serial.println("Connected! IP: " + WiFi.localIP().toString());

  // Serve static files from LittleFS
  server.serveStatic("/", LittleFS, "/").setDefaultFile("index.html");

  // LED toggle endpoint
  server.on("/led/toggle", HTTP_GET, [](AsyncWebServerRequest *request) {
    static bool ledState = false;
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState ? LOW : HIGH);
    request->send(200, "text/plain", ledState ? "ON" : "OFF");
  });

  // Board info endpoint
  server.on("/api/info", HTTP_GET, [](AsyncWebServerRequest *request) {
    String json = "{\"ip\":\"" + WiFi.localIP().toString() +
                  "\",\"ssid\":\"" + WiFi.SSID() +
                  "\",\"rssi\":" + String(WiFi.RSSI()) +
                  ",\"chip\":\"ESP8266\",\"heap\":" + String(ESP.getFreeHeap()) + "}";
    request->send(200, "application/json", json);
  });

  // OTA trigger (for future use)
  server.on("/api/ota", HTTP_POST, [](AsyncWebServerRequest *request) {
    request->send(200, "text/plain", "OTA not implemented in this firmware version");
  });

  server.onNotFound([](AsyncWebServerRequest *request) {
    request->send(404, "text/plain", "Not found");
  });

  server.begin();

  // Success blink: 2 short pulses
  ledPulse(2, 100, 100);
  Serial.println("HTTP server started on port 80");
}

void loop() {
  delay(10);
}
