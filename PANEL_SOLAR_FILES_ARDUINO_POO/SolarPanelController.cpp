#include "SolarPanelController.h"

SolarPanelController::SolarPanelController(
    WiFiManager& wifi,
    ServoController& servo,
    LightSensor& ldr,
    NubladoManager& nublado,
    SolarPanelShadow& shadow,
    unsigned long updateInterval,
    unsigned long recalibrarInterval
)
    : wifi(wifi), servo(servo), ldr(ldr), nublado(nublado), shadow(shadow),
      updateInterval(updateInterval), recalibrarInterval(recalibrarInterval),
      lastUpdateTime(0), recalibrar(false), lastLightLevel(""), lastIntensity(-1),
      lastNublado(false), busquedasMedio(0)
{}

void SolarPanelController::begin() {
    wifi.connect();
    servo.begin(0);
    ldr.begin();
    int initialIntensity = ldr.readIntensity();
    String initialLevel = ldr.getLevel(initialIntensity);
    publishState(initialLevel, initialIntensity, nublado.isNublado(), false, servo.getPosition());
    lastLightLevel = initialLevel;
    lastIntensity = initialIntensity;
    lastNublado = nublado.isNublado();
    Serial.print("Nivel inicial de luz: ");
    Serial.println(initialLevel);
}

void SolarPanelController::publishState(const String& lightLevel, int intensity, bool nublado, bool recalibrarShadow, int servoPosition) {
    String jsonPayload;
    shadow.buildStateJson(jsonPayload, lightLevel, intensity, nublado, recalibrarShadow, servoPosition);
    // Aquí publicarías el estado a AWS IoT (por MQTT, etc.) usando tu propia lógica de MQTT.
    // Por ejemplo: mqttClient.publish(topic, jsonPayload.c_str());
    Serial.print("Publicando estado: ");
    Serial.println(jsonPayload);
}

void SolarPanelController::handleShadowMessage(char* topic, byte* payload, unsigned int length) {
    payload[length] = '\0';
    StaticJsonDocument<1024> doc;
    DeserializationError error = deserializeJson(doc, payload);
    if (error) return;
    if (SolarPanelShadow::findRecalibracionTrue(doc)) {
        recalibrar = true;
        Serial.println("Recalibracion detectada en update del shadow.");
    }
}

void SolarPanelController::loop() {
    unsigned long now = millis();
    if (now - lastUpdateTime < updateInterval) return;
    lastUpdateTime = now;

    int currentIntensity = ldr.readIntensity();
    String currentLevel = ldr.getLevel(currentIntensity);

    if (recalibrar) {
        servo.setPosition(0);
        recalibrar = false;
        Serial.println("Recalibración ejecutada: servo a posición 0");
        publishState(currentLevel, currentIntensity, nublado.isNublado(), false, servo.getPosition());
        delay(500);
    }

    if (nublado.isNublado()) {
        if (currentLevel == "alto" || currentLevel == "bajo") {
            nublado.setNublado(false);
            publishState(currentLevel, currentIntensity, false, false, servo.getPosition());
            Serial.println("Cambio de estado detectado, saliendo de nublado.");
            lastLightLevel = currentLevel;
            lastIntensity = currentIntensity;
            lastNublado = false;
            busquedasMedio = 0;
            return;
        }
        nublado.update(now, recalibrarInterval, servo);
        return;
    }

    if (currentLevel != lastLightLevel) {
        if (currentLevel == "bajo") {
            servo.setPosition(0);
            Serial.println("Nivel bajo: panel a posición inicial.");
            busquedasMedio = 0;
            publishState(currentLevel, currentIntensity, false, false, servo.getPosition());
        }
        else if (currentLevel == "medio") {
            Serial.println("Nivel medio: iniciando búsqueda de luz alta.");
            busquedasMedio = 0;
            publishState(currentLevel, currentIntensity, false, false, servo.getPosition());
        }
        else if (currentLevel == "alto") {
            Serial.println("Nivel alto: manteniendo posición.");
            busquedasMedio = 0;
            publishState(currentLevel, currentIntensity, false, false, servo.getPosition());
        }
        lastLightLevel = currentLevel;
        lastIntensity = currentIntensity;
        lastNublado = nublado.isNublado();
    }

    if (currentLevel == "medio") {
        if (busquedasMedio < 9) {
            servo.increment(20);
            Serial.print("Buscando alto, ángulo: "); Serial.println(servo.getPosition());
            busquedasMedio++;
        } else if (!nublado.isNublado()) {
            nublado.setNublado(true);
            nublado.reset(now);
            publishState(currentLevel, currentIntensity, true, false, servo.getPosition());
            Serial.println("Día nublado detectado. Avanza servo cada 30s hasta cambio de estado.");
            lastNublado = true;
        }
    }
}