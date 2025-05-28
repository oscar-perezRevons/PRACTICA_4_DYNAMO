#include "NubladoManager.h"

NubladoManager::NubladoManager(unsigned long interval)
    : nublado(false), lastCheck(0), interval(interval) {}

bool NubladoManager::isNublado() const { return nublado; }
void NubladoManager::setNublado(bool value) { nublado = value; }
unsigned long NubladoManager::getLastCheck() const { return lastCheck; }
void NubladoManager::setLastCheck(unsigned long t) { lastCheck = t; }
unsigned long NubladoManager::getInterval() const { return interval; }