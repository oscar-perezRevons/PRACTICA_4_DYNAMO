#pragma once
#include <ArduinoJson.h>

class SolarPanelShadow {
public:
    SolarPanelShadow();
    void buildStateJson(
        String& outputJson,
        const String& lightLevel,
        int intensity,
        bool nublado,
        bool recalibrar,
        int servoPosition
    );
    static bool findRecalibracionTrue(JsonVariant v);
};