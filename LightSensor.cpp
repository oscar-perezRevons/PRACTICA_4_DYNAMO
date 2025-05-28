#include "LightSensor.h"
#include <Arduino.h> // Necesario para String y analogRead

LightSensor::LightSensor(int pin, const int *thresholds)
    : pin(pin), thresholds(thresholds) {}

int LightSensor::read() { return analogRead(pin); }

String LightSensor::getLevel(int value)
{
  if (value < thresholds[0])
    return "bajo";
  else if (value < thresholds[1])
    return "medio";
  else
    return "alto";
}