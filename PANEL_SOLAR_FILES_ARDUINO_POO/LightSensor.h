#pragma once
#include <Arduino.h>

class LightSensor {
public:
    LightSensor(int pin, int thresholdLow, int thresholdHigh);
    void begin();
    int readIntensity();
    String getLevel(int intensity);
private:
    int pin;
    int thresholdLow;
    int thresholdHigh;
};