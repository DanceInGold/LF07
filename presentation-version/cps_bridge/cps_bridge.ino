#include <Servo.h>
#include <U8g2lib.h>
#include <Wire.h>

// U8g2 Page-Buffer Modus (spart RAM)
U8G2_SH1106_128X64_NONAME_1_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);

// Pin-Definitionen (Stripper-Pins strikt der Reihe nach!)
const int SERVO_PIN = 3;
const int TRIG_PIN = 4;
const int ECHO_PIN = 5;
const int IN1 = 8;
const int IN2 = 9;
const int IN3 = 10;
const int IN4 = 11; 

Servo myServo;

String currentTime = "00:00";
String countdown = "00:00";

// --- CUSTOM HALF-STEP FUNKTION FÜR 28BYJ-48 ---
void moveSmooth(long steps) {
  // 8-Schritt-Matrix für butterweiche Bewegungen
  const byte stepSequence[8][4] = {
    {1,0,0,0}, {1,1,0,0}, {0,1,0,0}, {0,1,1,0},
    {0,0,1,0}, {0,0,1,1}, {0,0,0,1}, {1,0,0,1}
  };
  
  // Python denkt 2048 = 360°. Im Half-Step sind es aber 4096. Daher * 2.
  long halfSteps = steps * 2; 
  long stepsLeft = abs(halfSteps);
  int direction = (halfSteps > 0) ? 1 : -1;
  static int currentStep = 0; 
  
  while(stepsLeft > 0) {
    currentStep += direction;
    if(currentStep > 7) currentStep = 0;
    if(currentStep < 0) currentStep = 7;
    
    digitalWrite(IN1, stepSequence[currentStep][0]);
    digitalWrite(IN2, stepSequence[currentStep][1]);
    digitalWrite(IN3, stepSequence[currentStep][2]);
    digitalWrite(IN4, stepSequence[currentStep][3]);
    
    // Geschwindigkeit: 1000 Mikrosekunden (1ms) pro Schritt. 
    // Falls du ihn schneller/langsamer willst, ändere diesen Wert (z.B. 800 für schneller, 1500 für langsamer)
    delayMicroseconds(1000); 
    stepsLeft--;
  }
  
  // Nach der Bewegung: Spulen stromlos schalten (Verhindert Überhitzen und Strom-Zusammenbrüche)
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

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
  
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
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
      long steps = command.substring(4).toInt();
      moveSmooth(steps); // Aufruf der neuen butterweichen Funktion
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