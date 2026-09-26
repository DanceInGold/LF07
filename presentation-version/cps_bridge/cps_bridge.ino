#include <Servo.h>
#include <Stepper.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>

// I2C SH1106 OLED Display Setup
#define i2c_Address 0x3c // Typische I2C Adresse für dieses Display
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1   // Kein Hardware-Reset-Pin
Adafruit_SH1106G display = Adafruit_SH1106G(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

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
  display.clearDisplay();
  
  // 1. Uhrzeit oben rechts (TextSize 1 = Standardgröße)
  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE);
  display.setCursor(95, 0);
  display.print(currentTime);
  
  // 2. Überschrift
  display.setCursor(0, 20);
  display.print("Naechste Ausgabe in...");
  
  // 3. Großer Timer mittig (TextSize 2 = Doppelte Größe)
  display.setTextSize(2);
  display.setCursor(35, 40);
  display.print(countdown);
  
  display.display(); // Zeichnet alles auf das Display
}

void setup() {
  Serial.begin(115200);
  
  // Display initialisieren
  // Wir verzögern kurz, um dem I2C Bus Zeit zu geben
  delay(250); 
  if(!display.begin(i2c_Address, true)) {
    // Falls das Display nicht gefunden wird, schicke eine Warnung an den seriellen Monitor
    Serial.println("WARNUNG: SH1106 nicht gefunden!");
  } else {
    display.clearDisplay();
    display.display();
    updateDisplay();
  }
  
  // Hardware initialisieren
  myServo.attach(SERVO_PIN);
  myServo.write(0); // Grundposition
  
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  myStepper.setSpeed(10); // Geschwindigkeit in RPM
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Entfernt unsichtbare Zeichen

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