#pragma once

#include <WiFi.h>

class WiFiManager
{
  const char *ssid;
  const char *password;

public:
  WiFiManager(const char *ssid, const char *pass);
  void connect();
};
