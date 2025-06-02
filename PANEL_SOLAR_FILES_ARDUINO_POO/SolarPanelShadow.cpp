#include "SolarPanelShadow.h"

SolarPanelShadow::SolarPanelShadow() {}

void SolarPanelShadow::buildStateJson(
    String& outputJson,
    const String& lightLevel,
    int intensity,
    bool nublado,
    bool recalibrar,
    int servoPosition
) {
    StaticJsonDocument<512> doc;
    JsonObject reported = doc.createNestedObject("state").createNestedObject("reported");
    reported["lightLevel"] = lightLevel;
    reported["intensity"] = intensity;
    reported["Nublado"] = nublado;
    reported["recalibracion"] = recalibrar;
    reported["servoPosition"] = servoPosition;
    reported["angleValue"] = servoPosition;
    serializeJson(doc, outputJson);
}

bool SolarPanelShadow::findRecalibracionTrue(JsonVariant v) {
    if (v.is<JsonObject>()) {
        for (JsonPair kv : v.as<JsonObject>()) {
            if (String(kv.key().c_str()) == "recalibracion") {
                if (kv.value().is<bool>() && kv.value() == true) return true;
            }
            if (findRecalibracionTrue(kv.value())) return true;
        }
    } else if (v.is<JsonArray>()) {
        for (JsonVariant vv : v.as<JsonArray>()) {
            if (findRecalibracionTrue(vv)) return true;
        }
    }
    return false;
}