#include <Servo.h>
#include <Stepper.h>
#include <U8g2lib.h>
#include <Wire.h>

// WICHTIG: Das '_1_' in der Mitte bedeutet Page-Buffer (spart ca. 900 Bytes RAM!)
U8G2_SH1106_128X64_NONAME_1_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);

// Pin-Definitionen
const int SERVO_PIN = 3;
const int TRIG_PIN = 4;
const int ECHO_PIN = 5;
const int IN1 = 8, IN2 = 10, IN3 = 9, IN4 = 11; 
const int STEPS_PER_REV = 2048; 

Servo myServo;
Stepper myStepper(STEPS_PER_REV, IN1, IN2, IN3, IN4);

// Globale Variablen
String currentTime = "00:00";
String countdown = "00:00";

// Die neue, RAM-sparende Zeichen-Methode
void updateDisplay() {
  u8g2.firstPage();
  do {
    u8g2.setFont(u8g2_font_ncenB08_tr); 
    u8g2.drawStr(95, 10, currentTime.c_str());
    
    u8g2.drawStr(10, 30, "Naechste Ausgabe in...");
    
    u8g2.setFont(u8g2_font_logisoso16_tr); 
    u8g2.drawStr(38, 55, countdown.c_str());
  } while ( u8g2.nextPage() );
}

void setup() {
  Serial.begin(115200);
  
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
      int angle = command.substring(4).toInt();
      myServo.write(angle);
      Serial.println("ACK:SRV");
    }
    else if (command.startsWith("STP:")) {
      int steps = command.substring(4).toInt();
      myStepper.step(steps);
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
  }
}