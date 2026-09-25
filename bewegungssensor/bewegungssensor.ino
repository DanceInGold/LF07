// ==========================================
// MEDIKAMENTENSPENDER - SENSOR SYSTEM
// HC-SR04 + HC-SR501
// Arduino UNO R3
// ==========================================

const int TRIG_PIN = 7;
const int ECHO_PIN = 8;
const int PIR_PIN = 6;


// ==========================================
// EINSTELLUNGEN
// ==========================================

// Hand muss mindestens 10 cm oder näher sein
const int HAND_DISTANCE = 10;

// Hand muss 2 Sekunden ununterbrochen dort bleiben
const unsigned long HAND_HOLD_TIME = 2000;


// ==========================================
// VARIABLEN
// ==========================================

// Person wurde durch PIR erkannt
bool personDetected = false;

// Hand ist gerade im Bereich
bool handInPosition = false;

// Hand wurde erfolgreich bestätigt
bool hand_ready = false;

// Zeitpunkt, an dem die Hand in Position kam
unsigned long handStartTime = 0;

// Letzter PIR-Zustand
bool lastMotionState = false;


// ==========================================
// HC-SR04 Abstand messen
// ==========================================

long measureDistance()
{
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);

    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);

    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH, 30000);

    if (duration == 0)
    {
        return -1;
    }

    long distance = duration * 0.034 / 2;

    return distance;
}


// ==========================================
// SETUP
// ==========================================

void setup()
{
    Serial.begin(9600);

    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    pinMode(PIR_PIN, INPUT);

    Serial.println("SENSORS_READY");
}


// ==========================================
// LOOP
// ==========================================

void loop()
{
    // ======================================
    // 1. PIR - PERSON ERKENNEN
    // ======================================

    bool motionDetected = digitalRead(PIR_PIN) == HIGH;


    if (motionDetected != lastMotionState)
    {
        if (motionDetected)
        {
            personDetected = true;

            Serial.println("MOTION:1");
            Serial.println("PERSON_READY");
        }
        else
        {
            personDetected = false;

            Serial.println("MOTION:0");
        }

        lastMotionState = motionDetected;
    }


    // ======================================
    // 2. HAND ERST NACH PERSONENERKENNUNG
    // ======================================

    if (personDetected && !hand_ready)
    {
        long distance = measureDistance();


        // Hand befindet sich innerhalb des Bereichs
        bool handCurrentlyInPosition =
            distance > 0 && distance <= HAND_DISTANCE;


        // ==================================
        // HAND KOMMT IN POSITION
        // ==================================

        if (handCurrentlyInPosition)
        {
            // Neuer Versuch
            if (!handInPosition)
            {
                handInPosition = true;

                // Timer startet
                handStartTime = millis();
            }


            // ==================================
            // PRÜFEN: 2 SEKUNDEN ERREICHT?
            // ==================================

            if (millis() - handStartTime >= HAND_HOLD_TIME)
            {
                // Jetzt erst wird die Hand erkannt!
                Serial.println("HAND_DETECTED");

                // Variable für andere Systeme
                hand_ready = true;

                Serial.println("HAND_READY:1");
                Serial.println("READY_FOR_DISPENSING");


                // ==================================
                // ABLAUF BEENDET
                // ==================================

                while (true)
                {
                    // Programm bleibt hier stehen
                }
            }
        }


        // ==================================
        // HAND WAR NICHT LANGE GENUG DA
        // ==================================

        else
        {
            if (handInPosition)
            {
                // Hand war vorher da,
                // hat aber keine 2 Sekunden geschafft.

                handInPosition = false;

                // Timer zurücksetzen
                handStartTime = 0;

                // KEIN HAND_DETECTED!
                // Der Versuch wird einfach verworfen.
            }
        }
    }


    delay(50);
}