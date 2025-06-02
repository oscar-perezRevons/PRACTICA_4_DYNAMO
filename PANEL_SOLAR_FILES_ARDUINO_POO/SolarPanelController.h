#pragma once
#include "WiFiManager.h"
#include "ServoController.h"
#include "LightSensor.h"
#include "NubladoManager.h"
#include "SolarPanelShadow.h"

class SolarPanelController {
public:
    SolarPanelController(
        WiFiManager& wifi,
        ServoController& servo,
        LightSensor& ldr,
        NubladoManager& nublado,
        SolarPanelShadow& shadow,
        unsigned long updateInterval,
        unsigned long recalibrarInterval
    );
    void begin();
    void loop();
    void handleShadowMessage(char* topic, byte* payload, unsigned int length);
private:
    WiFiManager& wifi;
    ServoController& servo;
    LightSensor& ldr;
    NubladoManager& nublado;
    SolarPanelShadow& shadow;
    unsigned long updateInterval;
    unsigned long recalibrarInterval;
    unsigned long lastUpdateTime;
    bool recalibrar;
    String lastLightLevel;
    int lastIntensity;
    bool lastNublado;
    int busquedasMedio;
    void publishState(const String& lightLevel, int intensity, bool nublado, bool recalibrarShadow, int servoPosition);
};