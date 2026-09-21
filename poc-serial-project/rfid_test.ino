                                                                                            
#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>

#define SS_PIN 10
#define RST_PIN 8
#define I2C_ADDRESS 0x3C
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

MFRC522 rfid(SS_PIN, RST_PIN);
Adafruit_SH1106G display = Adafruit_SH1106G(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();

  if(!display.begin(I2C_ADDRESS, true)) {
    Serial.println("Display_Error");
    for(;;);
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE);
  display.setCursor(0, 10);
  display.println("System Bereit");
  display.display();
}

void loop() {
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String uidString = "UID:";
    for (byte i = 0; i < rfid.uid.size; i++) {
      uidString += String(rfid.uid.uidByte[i] < 0x10 ? "0" : "");
      uidString += String(rfid.uid.uidByte[i], HEX);
    }
    uidString.toUpperCase();
    Serial.println(uidString);

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
    delay(500);
  }
  
  if (Serial.available() > 0) {
    // Lies die Nachricht ein
    String message = Serial.readStringUntil('\n');

    // Suche nach einem Trennzeichen '|' für mehrzeiligen Text (hilft für den Countdown)
    int splitIndex = message.indexOf('|');

    display.clearDisplay(); // WICHTIG: Immer zuerst löschen!
    display.setTextSize(1);
    display.setTextColor(SH110X_WHITE);
    display.setCursor(0, 10);

    if (splitIndex != -1) {
      // Zeile 1
      display.println(message.substring(0, splitIndex));
      // Zeile 2 (z.B. der Countdown)
      display.println(message.substring(splitIndex + 1));
    } else {
      display.println(message);
    }

    display.display();
  }
}

