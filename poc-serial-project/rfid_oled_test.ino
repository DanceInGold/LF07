#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>

#define SS_PIN 10
#define RST_PIN 9

#define GREEN_LED 6
#define RED_LED 7
#define BUZZER 8

MFRC522 rfid(SS_PIN, RST_PIN);

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_I2C_ADDRESS 0x3C

Adafruit_SH1106G display = Adafruit_SH1106G(
  SCREEN_WIDTH,
  SCREEN_HEIGHT,
  &Wire,
  -1
);

void setup() {

  Serial.begin(9600);

  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED, LOW);
  noTone(BUZZER);

  SPI.begin();
  rfid.PCD_Init();

  delay(100);

  if (!display.begin(OLED_I2C_ADDRESS, true)) {
    Serial.println("OLED nicht gefunden!");
    while (true);
  }

  display.clearDisplay();
  display.setTextColor(SH110X_WHITE);
  display.display();

  Serial.println("UI TEST READY");
}

void loop() {

  // Warten, bis ein RFID-Chip erkannt wird
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }

  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }

  // UID des Chips auslesen
  String uid = "";

  for (byte i = 0; i < rfid.uid.size; i++) {

    if (rfid.uid.uidByte[i] < 0x10) {
      uid += "0";
    }

    uid += String(rfid.uid.uidByte[i], HEX);
  }

  uid.toUpperCase();

  Serial.print("UID: ");
  Serial.println(uid);

  // Test-UID
  // Wird später durch die echte Berechtigung ersetzt.
  String autorisierteUID = "0C18134A";

  display.clearDisplay();
  display.setTextColor(SH110X_WHITE);

  display.setTextSize(1);
  display.setCursor(40, 0);
  display.println("DISPENSER");

  // =====================================
  // ZUGRIFF ERLAUBT
  // =====================================

  if (uid == autorisierteUID) {

    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);

    // Positiver Ton
    tone(BUZZER, 1000);
    delay(250);
    noTone(BUZZER);

    Serial.println("ZUGRIFF ERLAUBT");

    display.setTextSize(2);

    display.setCursor(5, 15);
    display.println("ZUGRIFF");

    display.setCursor(10, 35);
    display.println("ERLAUBT");

    display.setTextSize(1);

    display.setCursor(25, 54);
    display.println("Naechste Dosis");
  }

  // =====================================
  // ZUGRIFF VERWEIGERT
  // =====================================

  else {

    digitalWrite(GREEN_LED, LOW);
    digitalWrite(RED_LED, HIGH);

    // Zwei tiefere Töne
    tone(BUZZER, 500);
    delay(200);
    noTone(BUZZER);

    delay(100);

    tone(BUZZER, 500);
    delay(300);
    noTone(BUZZER);

    Serial.println("ZUGRIFF VERWEIGERT");

    display.setTextSize(2);

    display.setCursor(5, 15);
    display.println("ZUGRIFF");

    display.setCursor(5, 35);
    display.println("VERWEIGERT");
  }

  // OLED anzeigen
  display.display();

  // =====================================
  // 5-SEKUNDEN-TIMER
  // =====================================

  unsigned long startZeit = millis();

  while (millis() - startZeit < 5000) {
    // Anzeige bleibt 5 Sekunden sichtbar
  }

  // =====================================
  // ALLES AUSSCHALTEN
  // =====================================

  display.clearDisplay();
  display.display();

  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED, LOW);
  noTone(BUZZER);

  // RFID-Chip zurücksetzen
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();

  // kurze Pause
  delay(500);
}
