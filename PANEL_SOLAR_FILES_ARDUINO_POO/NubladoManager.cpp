#include "NubladoManager.h"

NubladoManager::NubladoManager() : nublado(false), lastMoveTime(0) {}

void NubladoManager::setNublado(bool isNublado) {
    nublado = isNublado;
}

bool NubladoManager::isNublado() const {
    return nublado;
}

void NubladoManager::update(unsigned long now, unsigned long intervalo, ServoController& servo) {
    if (now - lastMoveTime >= intervalo) {
        servo.increment(20);
        if (servo.getPosition() > 180) servo.setPosition(0);
        lastMoveTime = now;
    }
}

void NubladoManager::reset(unsigned long now) {
    lastMoveTime = now;
}