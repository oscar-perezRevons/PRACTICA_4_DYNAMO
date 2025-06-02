#pragma once
#include <ESP32Servo.h>

class ServoController {
public:
    ServoController(int pin);
    void begin(int initialPos = 0);
    void setPosition(int pos);
    int getPosition() const;
    void increment(int step);
private:
    Servo servo;
    int pin;
    int position;
};