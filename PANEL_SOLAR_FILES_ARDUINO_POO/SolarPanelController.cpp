#include "SolarPanelController.h"
#include <ArduinoJson.h>
#include <Arduino.h>

// certificados.h ya está incluido desde el header

SolarPanelController::SolarPanelController(
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
    unsigned long updateInterval)
    : wifi(wifi_ssid, wifi_pass),
      client(net),
      servo(servoPin),
      sensor(ldrPin, thresholds),
      MQTT_BROKER(mqtt_broker),
      MQTT_PORT(mqtt_port),
      CLIENT_ID(client_id),
      SHADOW_UPDATE_TOPIC(shadow_update_topic),
      SHADOW_GET_TOPIC(shadow_get_topic),
      lastUpdateTime(0),
      updateInterval(updateInterval),
      mediumSweepDegrees(0)
{
}

void SolarPanelController::begin()
{
  Serial.begin(115200);
  wifi.connect();

  net.setCACert(AMAZON_ROOT_CA1);
  net.setCertificate(CERTIFICATE);
  net.setPrivateKey(PRIVATE_KEY);

  client.setServer(MQTT_BROKER, MQTT_PORT);
  client.setCallback([this](char *topic, byte *payload, unsigned int length)
                     { this->mqttCallback(topic, payload, length); });

  connectAWS();

  servo.begin();
  int initialIntensity = sensor.read();
  String initialLevel = sensor.getLevel(initialIntensity);
  Serial.print("Nivel inicial de luz: ");
  Serial.println(initialLevel);
  shadow.update(client, SHADOW_UPDATE_TOPIC, initialIntensity, initialLevel, servo.getPosition(), nubladoMgr.isNublado());
}

void SolarPanelController::loop()
{
  if (!client.connected())
    connectAWS();
  client.loop();

  handleNubladoMode();

  if (nubladoMgr.isNublado())
  {
    shadow.update(client, SHADOW_UPDATE_TOPIC, sensor.read(), sensor.getLevel(sensor.read()), servo.getPosition(), true);
    delay(100);
    return;
  }

  if (millis() - lastUpdateTime >= updateInterval)
  {
    int currentIntensity = sensor.read();
    String currentLevel = sensor.getLevel(currentIntensity);
    controlServo(currentLevel);
    shadow.update(client, SHADOW_UPDATE_TOPIC, currentIntensity, currentLevel, servo.getPosition(), nubladoMgr.isNublado());
    lastUpdateTime = millis();
  }
}

void SolarPanelController::connectAWS()
{
  Serial.print("Conectando a AWS IoT...");
  while (!client.connected())
  {
    if (client.connect(CLIENT_ID))
    {
      Serial.println("Conectado.");
      client.subscribe(SHADOW_GET_TOPIC);
    }
    else
    {
      Serial.print(".");
      delay(1000);
    }
  }
}

void SolarPanelController::mqttCallback(char *topic, byte *payload, unsigned int length)
{
  Serial.print("Mensaje recibido [");
  Serial.print(topic);
  Serial.println("]");
  if (String(topic) == SHADOW_GET_TOPIC)
  {
    int currentIntensity = sensor.read();
    String currentLevel = sensor.getLevel(currentIntensity);
    shadow.update(client, SHADOW_UPDATE_TOPIC, currentIntensity, currentLevel, servo.getPosition(), nubladoMgr.isNublado());
  }
}

void SolarPanelController::controlServo(String lightLevel)
{
  unsigned long currentTime = millis();
  if (nubladoMgr.isNublado())
    return;

  if (lightLevel == "bajo")
  {
    if (servo.getPosition() != 0)
    {
      servo.moveToLow();
    }
    mediumSweepDegrees = 0;
  }
  else if (lightLevel == "medio" && (currentTime - servo.getLastMoveTime() >= servo.getDelayMs()))
  {
    servo.moveToNextMedium();
    mediumSweepDegrees += servo.getIncrement();
    if (mediumSweepDegrees >= 180)
    {
      nubladoMgr.setNublado(true);
      nubladoMgr.setLastCheck(millis());
      Serial.println("Modo nublado activado: no se encontró 'alto' en una vuelta.");
      mediumSweepDegrees = 0;
    }
    servo.setLastMoveTime(currentTime);
  }
  else if (lightLevel == "alto")
  {
    servo.stayHigh();
    mediumSweepDegrees = 0;
  }
}

void SolarPanelController::handleNubladoMode()
{
  if (!nubladoMgr.isNublado())
    return;
  unsigned long currentTime = millis();
  if (currentTime - nubladoMgr.getLastCheck() >= nubladoMgr.getInterval())
  {
    Serial.println("Recalibración en modo nublado...");
    int intensity = sensor.read();
    String level = sensor.getLevel(intensity);
    if (level == "alto")
    {
      nubladoMgr.setNublado(false);
      mediumSweepDegrees = 0;
      Serial.println("¡Se encontró 'alto'! Saliendo de modo nublado.");
    }
    nubladoMgr.setLastCheck(currentTime);
  }
}