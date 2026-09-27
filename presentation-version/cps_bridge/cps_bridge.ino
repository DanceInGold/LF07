#include <Servo.h>

// Pin-Definitionen
const int SERVO_PIN = 3;
const int TRIG_PIN = 4;
const int ECHO_PIN = 5;
const int IN1 = 8;
const int IN2 = 9;
const int IN3 = 10;
const int IN4 = 11; 

Servo myServo;

// --- CUSTOM POWER FUNKTION (Full-Step, Dual Coil) ---
void movePower(long steps) {
  // 4-Schritt-Matrix: Es stehen immer exakt 2 Spulen unter Strom.
  // Das liefert das absolute Maximum an Drehmoment für diesen Motor.
  const byte stepSequence[4][4] = {
    {1,1,0,0}, 
    {0,1,1,0}, 
    {0,0,1,1}, 
    {1,0,0,1}
  };
  
  // Im Full-Step-Modus entsprechen 360° wieder exakt 2048 Schritten.
  // Die Umrechnung (* 2) aus dem Half-Step-Code entfällt hier.
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
    
    // Geschwindigkeit auf 2500 Mikrosekunden (2,5ms) gesenkt. 
    // Der Motor dreht langsamer, hat dadurch aber deutlich mehr Biss.
    delayMicroseconds(3000); 
    stepsLeft--;
  }
  
  // Motoren nach der Bewegung zwingend stromlos schalten
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void setup() {
  Serial.begin(115200);
  
  myServo.attach(SERVO_PIN);
  myServo.write(0);
  
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // Stepper Pins
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); 

    if (command.startsWith("SRV:")) {
      int angle = command.substring(4).toInt();
      myServo.write(angle);
      Serial.println("ACK:SRV");
    }
    else if (command.startsWith("STP:")) {
      long steps = command.substring(4).toInt();
      movePower(steps); // Aufruf der neuen Power-Funktion
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