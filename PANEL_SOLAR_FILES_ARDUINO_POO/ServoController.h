#pragma once

#include <ESP32Servo.h>

class ServoController
{
  Servo servo;
  int pin;
  int pos;
  int increment;
  unsigned long lastMoveTime;
  int sweepDegrees;
  int delayMs;

public:
  ServoController(int pin, int increment = 20, int delayMs = 3000);
  void begin();
  int getPosition() const;
  void setPosition(int newPos);
  void resetSweep();
  void incrementSweep();
  void resetSweepDegrees();
  int getSweepDegrees() const;
  void setLastMoveTime(unsigned long t);
  unsigned long getLastMoveTime() const;
  int getIncrement() const;
  int getDelayMs() const;
  void moveToLow();
  void moveToNextMedium();
  void stayHigh();
};