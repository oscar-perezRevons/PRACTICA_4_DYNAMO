#pragma once
#include <Arduino.h>

class LightSensor
{
  int pin;
  const int *thresholds;

public:
  LightSensor(int pin, const int *thresholds);
  int read();
  String getLevel(int value); // Cambia string -> String
};