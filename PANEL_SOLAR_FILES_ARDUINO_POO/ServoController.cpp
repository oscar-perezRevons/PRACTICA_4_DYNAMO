#include "ServoController.h"

ServoController::ServoController(int pin, int increment, int delayMs)
    : pin(pin), pos(0), increment(increment),
      lastMoveTime(0), sweepDegrees(0), delayMs(delayMs) {}

void ServoController::begin()
{
  servo.attach(pin);
  servo.write(pos);
}

int ServoController::getPosition() const { return pos; }

void ServoController::setPosition(int newPos)
{
  pos = constrain(newPos, 0, 180);
  servo.write(pos);
}

void ServoController::resetSweep() { sweepDegrees = 0; }

void ServoController::incrementSweep() { sweepDegrees += increment; }

void ServoController::resetSweepDegrees() { sweepDegrees = 0; }

int ServoController::getSweepDegrees() const { return sweepDegrees; }

void ServoController::setLastMoveTime(unsigned long t) { lastMoveTime = t; }

unsigned long ServoController::getLastMoveTime() const { return lastMoveTime; }

int ServoController::getIncrement() const { return increment; }

int ServoController::getDelayMs() const { return delayMs; }

void ServoController::moveToLow()
{
  setPosition(0);
  Serial.println("Luz baja: servo a posición 0°.");
  resetSweepDegrees();
}

void ServoController::moveToNextMedium()
{
  pos += increment;
  if (pos > 180)
    pos = 0;
  setPosition(pos);
  Serial.print("Buscando 'alto' en 'medio': servo a ");
  Serial.print(pos);
  Serial.println("°.");
  incrementSweep();
}

void ServoController::stayHigh()
{
  Serial.println("Luz 'alto': manteniendo posición.");
  resetSweepDegrees();
}