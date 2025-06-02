#include "ServoController.h"

ServoController::ServoController(int pin) : pin(pin), position(0) {}

void ServoController::begin(int initialPos) {
    servo.attach(pin);
    setPosition(initialPos);
}

void ServoController::setPosition(int pos) {
    position = pos;
    if (position < 0) position = 0;
    if (position > 180) position = 180;
    servo.write(position);
}

int ServoController::getPosition() const {
    return position;
}

void ServoController::increment(int step) {
    setPosition(position + step);
}