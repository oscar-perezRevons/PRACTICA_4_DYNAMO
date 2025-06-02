#pragma once

class Certificados {
public:
    static const char* getRootCA();
    static const char* getCertificate();
    static const char* getPrivateKey();
};