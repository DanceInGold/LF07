#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define SS_PIN 10
#define RST_PIN 9
#define BUZZER_PIN 7

MFRC522 rfid(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x27, 16, 2);

String erlaubteUID = "53FBEB12";

void setup() {

  Serial.begin(9600);

  SPI.begin();
  rfid.PCD_Init();

  pinMode(BUZZER_PIN, OUTPUT);

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0,0);
  lcd.print("MHTF");

  lcd.setCursor(0,1);
  lcd.print("Bitte scannen");
}

void loop() {

  if (!rfid.PICC_IsNewCardPresent())
    return;

  if (!rfid.PICC_ReadCardSerial())
    return;

  String uid = "";

  for (byte i = 0; i < rfid.uid.size; i++) {

    if (rfid.uid.uidByte[i] < 0x10)
      uid += "0";

    uid += String(rfid.uid.uidByte[i], HEX);
  }

  uid.toUpperCase();

  Serial.print("UID erkannt: ");
  Serial.println(uid);

  lcd.clear();

unsigned long start = millis();

while (!Serial.available()) {

    if (millis() - start > 3000) {

        lcd.setCursor(0,0);
        lcd.print("Keine Antwort");

        delay(2000);

        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("MHTF");
        lcd.setCursor(0,1);
        lcd.print("Bitte scannen");

        return;
    }
}

String antwort = Serial.readStringUntil('\n');
antwort.trim();

if (antwort == "ALLOW") {

    lcd.setCursor(0,0);
    lcd.print("Zugriff");

    lcd.setCursor(0,1);
    lcd.print("ERLAUBT");

    tone(BUZZER_PIN, 1200);
    delay(500);
    noTone(BUZZER_PIN);

}
else {

    lcd.setCursor(0,0);
    lcd.print("Zugriff");

    lcd.setCursor(0,1);
    lcd.print("VERWEIGERT");

    for(int i = 0; i < 3; i++) {

        tone(BUZZER_PIN, 400);
        delay(150);
        noTone(BUZZER_PIN);
        delay(150);
    }
}
  delay(3000);

  lcd.clear();

  lcd.setCursor(0,0);
  lcd.print("MHTF");

  lcd.setCursor(0,1);
  lcd.print("Bitte scannen");

  rfid.PICC_HaltA();
}
