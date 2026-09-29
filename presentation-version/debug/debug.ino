#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN 9
#define SS_PIN 10
MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
  while (!Serial); // Kurz warten, bis der Serielle Port bereit ist
  
  SPI.begin();
  mfrc522.PCD_Init();
  
  Serial.println("-----------------------------------");
  Serial.println("RFID Scanner bereit!");
  Serial.println("Bitte einen Chip an den Leser halten...");
  Serial.println("-----------------------------------");
}

void loop() {
  // Sucht nach neuen Karten
  if ( ! mfrc522.PICC_IsNewCardPresent()) {
    return;
  }
  
  // Liest die Karte aus
  if ( ! mfrc522.PICC_ReadCardSerial()) {
    return;
  }
  
  // UID im Seriellen Monitor ausgeben
  Serial.print("Chip erkannt! UID: ");
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
    Serial.print(mfrc522.uid.uidByte[i], HEX);
  }
  Serial.println();
  
  // Karte "schlafenlegen"
  mfrc522.PICC_HaltA();
}