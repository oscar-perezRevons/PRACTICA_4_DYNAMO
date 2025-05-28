#pragma once

#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include "WiFiManager.h"
#include "ServoController.h"
#include "LightSensor.h"
#include "SolarPanelShadow.h"
#include "NubladoManager.h"
#include "certificados.h" // <--- Incluye aquí los certificados

class SolarPanelController
{
  WiFiManager wifi;
  WiFiClientSecure net;
  PubSubClient client;
  ServoController servo;
  LightSensor sensor;
  SolarPanelShadow shadow;
  NubladoManager nubladoMgr;

  const char *MQTT_BROKER;
  int MQTT_PORT;
  const char *CLIENT_ID;
  const char *SHADOW_UPDATE_TOPIC;
  const char *SHADOW_GET_TOPIC;

  unsigned long lastUpdateTime;
  unsigned long updateInterval;
  int mediumSweepDegrees;

public:
  SolarPanelController(
      const char *wifi_ssid,
      const char *wifi_pass,
      int ldrPin,
      const int *thresholds,
      int servoPin,
      const char *mqtt_broker,
      int mqtt_port,
      const char *client_id,
      const char *shadow_update_topic,
      const char *shadow_get_topic,
      unsigned long updateInterval = 3000);

  void begin();
  void loop();

private:
  void connectAWS();
  void mqttCallback(char *topic, byte *payload, unsigned int length);
  void controlServo(String lightLevel);
  void handleNubladoMode();
};