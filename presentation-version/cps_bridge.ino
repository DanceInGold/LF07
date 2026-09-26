#include <Servo.h>
#include <Stepper.h>
#include <U8g2lib.h>
#include <Wire.h>

// I2C SH1106 OLED Display Setup
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);

// Pin-Definitionen
const int SERVO_PIN = 3;
const int TRIG_PIN = 4;
const int ECHO_PIN = 5;
const int IN1 = 8, IN2 = 10, IN3 = 9, IN4 = 11; 
const int STEPS_PER_REV = 2048; 

Servo myServo;
Stepper myStepper(STEPS_PER_REV, IN1, IN2, IN3, IN4);

// Globale Variablen für das Display
String currentTime = "00:00";
String countdown = "00:00";

void updateDisplay() {
  u8g2.clearBuffer();
  
  // 1. Uhrzeit oben rechts
  u8g2.setFont(u8g2_font_ncenB08_tr); 
  u8g2.drawStr(95, 10, currentTime.c_str());
  
  // 2. Überschrift (Wir nutzen "ae" statt "ä" um ASCII-Font-Probleme zu vermeiden)
  u8g2.drawStr(10, 30, "Naechste Ausgabe in...");
  
  // 3. Großer Timer mittig
  u8g2.setFont(u8g2_font_logisoso16_tr); // Schöne große, gut lesbare Schrift
  u8g2.drawStr(38, 55, countdown.c_str());
  
  u8g2.sendBuffer(); // Zeichnet alles auf das Display
}

void setup() {
  Serial.begin(115200);
  
  // Display initialisieren
  u8g2.begin();
  updateDisplay();
  
  myServo.attach(SERVO_PIN);
  myServo.write(0);
  
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  myStepper.setSpeed(10);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    // --- OLED UPDATE ---
    if (command.startsWith("OLED:")) {
      String data = command.substring(5);
      int sepIdx = data.indexOf('|');
      if (sepIdx != -1) {
        currentTime = data.substring(0, sepIdx);
        countdown = data.substring(sepIdx + 1);
        updateDisplay();
      }
      Serial.println("ACK:OLED");
    }
    
    // --- SERVO STEUERUNG ---
    else if (command.startsWith("SRV:")) {
      int angle = command.substring(4).toInt();
      myServo.write(angle);
      Serial.println("ACK:SRV");
    }
    
    // --- STEPPER STEUERUNG ---
    else if (command.startsWith("STP:")) {
      int steps = command.substring(4).toInt();
      myStepper.step(steps);
      Serial.println("ACK:STP");
    }
    
    // --- ULTRASCHALL ABFRAGE ---
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
  }
}