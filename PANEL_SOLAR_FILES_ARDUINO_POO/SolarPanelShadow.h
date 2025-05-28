#pragma once

#include <PubSubClient.h>

class SolarPanelShadow
{
  String previousLightLevel;
  bool lastNublado;

public:
  SolarPanelShadow();
  void update(PubSubClient &client, const char *topic,
              int currentIntensity, String currentLevel,
              int currentServoPos, bool nublado);
};