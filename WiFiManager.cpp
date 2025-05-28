#include "WiFiManager.h"

WiFiManager::WiFiManager(const char *ssid, const char *pass)
    : ssid(ssid), password(pass) {}

void WiFiManager::connect()
{
  Serial.print("Conectando a WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado.");
}