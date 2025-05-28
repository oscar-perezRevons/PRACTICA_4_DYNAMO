#include "SolarPanelShadow.h"
#include <ArduinoJson.h>
#include <Arduino.h>

SolarPanelShadow::SolarPanelShadow()
    : previousLightLevel(""), lastNublado(false) {}

void SolarPanelShadow::update(PubSubClient &client, const char *topic,
                              int currentIntensity, String currentLevel,
                              int currentServoPos, bool nublado)
{
  StaticJsonDocument<512> doc;
  JsonObject desired = doc.createNestedObject("state").createNestedObject("desired");
  desired["lightLevel"] = currentLevel;
  desired["intensity"] = currentIntensity;
  desired["angleValue"] = currentServoPos;
  desired["Nublado"] = nublado;
  JsonObject reported = doc["state"].createNestedObject("reported");
  reported["lightLevel"] = currentLevel;
  reported["intensity"] = currentIntensity;
  reported["timestamp"] = millis();
  reported["angleValue"] = currentServoPos;
  reported["Nublado"] = nublado;

  char jsonBuffer[768];
  serializeJson(doc, jsonBuffer);

  if (currentLevel != previousLightLevel || lastNublado != nublado)
  {
    if (client.publish(topic, jsonBuffer))
    {
      Serial.print("Nivel de luz: ");
      Serial.print(currentLevel);
      Serial.print(" (");
      Serial.print(currentIntensity);
      Serial.print(") - Ángulo: ");
      Serial.print(currentServoPos);
      Serial.print("° - Nublado: ");
      Serial.println(nublado ? "True" : "False");
      previousLightLevel = currentLevel;
      lastNublado = nublado;
    }
    else
    {
      Serial.println("Error al publicar en MQTT");
    }
  }
}