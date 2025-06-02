#include "LightSensor.h"

LightSensor::LightSensor(int pin, int thresholdLow, int thresholdHigh)
    : pin(pin), thresholdLow(thresholdLow), thresholdHigh(thresholdHigh) {}

void LightSensor::begin() {
    // No special init for analog input on ESP32
}

int LightSensor::readIntensity() {
    return analogRead(pin);
}

String LightSensor::getLevel(int intensity) {
    if (intensity < thresholdLow) return "bajo";
    else if (intensity < thresholdHigh) return "medio";
    else return "alto";
}