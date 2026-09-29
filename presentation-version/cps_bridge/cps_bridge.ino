#include <Servo.h>
#include <SPI.h>
#include <MFRC522.h>

// RFID Setup
#define RST_PIN 9
#define SS_PIN 10
MFRC522 mfrc522(SS_PIN, RST_PIN);
String lastScannedUID = "";

// Pin-Definitionen
const int SERVO1_PIN = 3; // Ausgabe-Schleuse
const int SERVO2_PIN = 6; // Nachfüll-Schloss
const int TRIG_PIN = 4;
const int ECHO_PIN = 5;

// Stepper auf Analog-Pins!
const int IN1 = A0;
const int IN2 = A1;
const int IN3 = A2;
const int IN4 = A3; 

Servo servo1;
Servo servo2;

void movePower(long steps) {
  const byte stepSequence[4][4] = {
    {1,1,0,0}, {0,1,1,0}, {0,0,1,1}, {1,0,0,1}
  };
  
  long stepsLeft = abs(steps);
  int direction = (steps > 0) ? 1 : -1;
  static int currentStep = 0; 
  
  while(stepsLeft > 0) {
    currentStep += direction;
    if(currentStep > 3) currentStep = 0;
    if(currentStep < 0) currentStep = 3;
    
    digitalWrite(IN1, stepSequence[currentStep][0]);
    digitalWrite(IN2, stepSequence[currentStep][1]);
    digitalWrite(IN3, stepSequence[currentStep][2]);
    digitalWrite(IN4, stepSequence[currentStep][3]);
    
    delayMicroseconds(3000); 
    stepsLeft--;
  }
  
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void setup() {
  Serial.begin(115200);
  
  // SPI & RFID initialisieren
  SPI.begin();
  mfrc522.PCD_Init();
  
  servo1.attach(SERVO1_PIN);
  servo1.write(0);
  
  servo2.attach(SERVO2_PIN);
  servo2.write(0); // 0 = Schloss zu
  
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
}

void loop() {
  // 1. Asynchron RFID checken (Blockiert den Code nicht)
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String uid = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
      uid += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
      uid += String(mfrc522.uid.uidByte[i], HEX);
    }
    uid.toUpperCase();
    lastScannedUID = uid;
    
    // Karte "schlafenlegen", damit sie nicht 100x pro Sekunde gelesen wird
    mfrc522.PICC_HaltA(); 
  }

  // 2. Befehle von Python verarbeiten
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); 

    if (command.startsWith("SRV:")) {
      int angle = command.substring(4).toInt();
      servo1.write(angle);
      Serial.println("ACK:SRV");
    }
    else if (command.startsWith("SRV2:")) {
      int angle = command.substring(5).toInt();
      servo2.write(angle);
      Serial.println("ACK:SRV2");
    }
    else if (command.startsWith("STP:")) {
      long steps = command.substring(4).toInt();
      movePower(steps); 
      Serial.println("ACK:STP");
    }
    else if (command == "US:GET") {
      digitalWrite(TRIG_PIN, LOW);
      delayMicroseconds(2);
      digitalWrite(TRIG_PIN, HIGH);
      delayMicroseconds(10);
      digitalWrite(TRIG_PIN, LOW);
      
      long duration = pulseIn(ECHO_PIN, HIGH, 30000); 
      float distance = (duration * 0.0343) / 2.0;
      Serial.print("DIST:");
      Serial.println(distance);
    }
    else if (command == "RFID:GET") {
      if (lastScannedUID != "") {
        Serial.println("RFID:" + lastScannedUID);
        lastScannedUID = ""; // Speicher nach Übermittlung leeren
      } else {
        Serial.println("RFID:NONE");
      }
    }
  }
}