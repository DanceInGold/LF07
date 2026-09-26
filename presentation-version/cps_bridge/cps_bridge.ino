#include <Servo.h>
#include <Stepper.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>

#define i2c_Address 0x3c 
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1   
Adafruit_SH1106G display = Adafruit_SH1106G(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

const int SERVO_PIN = 3;
const int TRIG_PIN = 4;
const int ECHO_PIN = 5;
const int IN1 = 8, IN2 = 10, IN3 = 9, IN4 = 11; 
const int STEPS_PER_REV = 2048; 

Servo myServo;
Stepper myStepper(STEPS_PER_REV, IN1, IN2, IN3, IN4);

String currentTime = "00:00";
String countdown = "00:00";

void updateDisplay() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE);
  display.setCursor(95, 0);
  display.print(currentTime);
  display.setCursor(0, 20);
  display.print("Naechste Ausgabe in...");
  display.setTextSize(2);
  display.setCursor(35, 40);
  display.print(countdown);
  display.display(); 
}

void setup() {
  Serial.begin(115200);
  delay(250); 
  
  if(display.begin(i2c_Address, true)) {
    display.clearDisplay();
    display.display();
    updateDisplay();
  }
  
  myServo.attach(SERVO_PIN);
  // myServo.write(0); <-- Entfernt, um Absturz beim Booten zu verhindern!
  
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  myStepper.setSpeed(10);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); 

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
    
    else if (command.startsWith("SRV:")) {
      Serial.println("ACK:SRV_START"); // NEU: Bestätigung VOR der Bewegung
      int angle = command.substring(4).toInt();
      myServo.write(angle);
      Serial.println("ACK:SRV_DONE");  // NEU: Bestätigung NACH der Bewegung
    }
    
    else if (command.startsWith("STP:")) {
      Serial.println("ACK:STP_START"); // NEU: Bestätigung VOR der Bewegung
      int steps = command.substring(4).toInt();
      myStepper.step(steps);
      Serial.println("ACK:STP_DONE");  // NEU: Bestätigung NACH der Bewegung
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
  }
}