#pragma once
#include "ServoController.h"

class NubladoManager {
public:
    NubladoManager();
    void setNublado(bool isNublado);
    bool isNublado() const;
    void update(unsigned long now, unsigned long intervalo, ServoController& servo);
    void reset(unsigned long now);
private:
    bool nublado;
    unsigned long lastMoveTime;
};