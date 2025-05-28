#include "SolarPanelController.h"
#include "certificados.h"

// ==== Configuración usuario ====
const char *WIFI_SSID = "LABO16";
const char *WIFI_PASS = "catolica16";
const int LDR_PIN = 34;
const int LDR_THRESHOLDS[] = {300, 700};
const int SERVO_PIN = 13;
const char *MQTT_BROKER = "a8zrduyiqifqz-ats.iot.us-east-2.amazonaws.com";
const int MQTT_PORT = 8883;
const char *CLIENT_ID = "ESP32-SolarPanel";
const char *SHADOW_UPDATE_TOPIC = "$aws/things/Panel_Objeto/shadow/update";
const char *SHADOW_GET_TOPIC = "$aws/things/Panel_Objeto/shadow/get";

SolarPanelController solarPanel(
    WIFI_SSID,
    WIFI_PASS,
    LDR_PIN,
    LDR_THRESHOLDS,
    SERVO_PIN,
    MQTT_BROKER,
    MQTT_PORT,
    CLIENT_ID,
    SHADOW_UPDATE_TOPIC,
    SHADOW_GET_TOPIC);

void setup()
{
  solarPanel.begin();
}

void loop()
{
  solarPanel.loop();
}