#include <Arduino.h>
#include "Certificados.h"
#include "WiFiManager.h"
#include "ServoController.h"
#include "LightSensor.h"
#include "NubladoManager.h"
#include "SolarPanelShadow.h"
#include "SolarPanelController.h"

// Configuración de pines y umbrales
const char* WIFI_SSID = "TECHLAB";
const char* WIFI_PASS = "catolica11";
const int LDR_PIN = 34;
const int SERVO_PIN = 13;
const int THRESHOLD_LOW = 300;
const int THRESHOLD_HIGH = 700;
const unsigned long INTERVALO_RECALIBRACION = 30000;
const unsigned long UPDATE_INTERVAL = 3000;

// Instancias globales de cada clase
WiFiManager wifi(WIFI_SSID, WIFI_PASS);
ServoController servo(SERVO_PIN);
LightSensor ldr(LDR_PIN, THRESHOLD_LOW, THRESHOLD_HIGH);
NubladoManager nublado;
SolarPanelShadow shadow;
SolarPanelController controller(
    wifi, servo, ldr, nublado, shadow, UPDATE_INTERVAL, INTERVALO_RECALIBRACION
);

void setup() {
    Serial.begin(115200);
    controller.begin();
    // Aquí deberías inicializar tu cliente MQTT y suscribirte,
    // y en el callback de MQTT llamar a controller.handleShadowMessage(...)
}

void loop() {
    controller.loop();
    // Aquí deberías hacer loop() de tu cliente MQTT si usas uno
}