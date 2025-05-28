#pragma once

class NubladoManager
{
  bool nublado;
  unsigned long lastCheck;
  unsigned long interval;

public:
  NubladoManager(unsigned long interval = 30000);
  bool isNublado() const;
  void setNublado(bool value);
  unsigned long getLastCheck() const;
  void setLastCheck(unsigned long t);
  unsigned long getInterval() const;
};