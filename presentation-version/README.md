# Projektdokumentation: Autonomes CPS-Medikamenten-Ausgabesystem

## 1. Projektübersicht

Das Projekt ist ein **Cyber-Physical System (CPS)** zur automatisierten, DSGVO-konformen und sicheren Ausgabe von Medikamenten. Es schlägt eine Brücke zwischen einer digitalen Web-Verwaltung (Software) und physischer Mechanik (Hardware). Das System liest JSON-basierte Medikamentenpläne aus, bereitet die Ausgabe asynchron durch mechanische Vorsortierung vor und gibt die Medikamente berührungslos über Sensoren aus. Eine RFID-gestützte Verriegelung sichert das Gerät vor unbefugtem Zugriff.

## 2. Hardware-Architektur & Pinout

Das System nutzt eine Master-Slave-Architektur. Der **Raspberry Pi (Master)** übernimmt die High-Level-Logik (JSON-Parsing, Scheduling, Display-Rendering), während der **Arduino (Slave / "Dumb Bridge")**ausschließlich für harte Echtzeit-Hardware-Steuerung zuständig ist.

### 2.1 Raspberry Pi (Master)

- **I2C OLED-Display (SH1106):**
    - VCC ➔ 3.3V (Pin 1) oder 5V (Pin 2)
    - GND ➔ GND (Pin 6)
    - SDA ➔ GPIO 2 (Pin 3)
    - SCL ➔ GPIO 3 (Pin 5)
- **USB-Verbindung:** Zum Arduino (für Serielle Kommunikation `/dev/ttyACM0`).

### 2.2 Arduino Uno/Nano (Hardware Bridge)

- **Stepper-Motor (28BYJ-48 via ULN2003) – Dosierungs-Schleuse:**
    - IN1 ➔ **A0** | IN2 ➔ **A1** | IN3 ➔ **A2** | IN4 ➔ **A3**
- **Ultraschallsensor (HC-SR04) – Hand-Erkennung:**
    - TRIG ➔ **Pin 4** | ECHO ➔ **Pin 5**
- **Servo 1 – Ausgabe-Schleuse:**
    - Signal ➔ **Pin 3**
- **Servo 2 – Nachfüll-Schloss:**
    - Signal ➔ **Pin 6**
- **RFID-Sensor (MFRC522) – Authentifizierung (SPI-Bus):**
    - VCC ➔ **3.3V** *(Zwingend!)* | GND ➔ GND
    - RST ➔ **Pin 9** | SDA (SS) ➔ **Pin 10** | MOSI ➔ **Pin 11** | MISO ➔ **Pin 12** | SCK ➔ **Pin 13**
- *Stromversorgungshinweis:* Um Brownouts zu verhindern, werden Servos im Idealfall über eine externe 5V-Quelle (mit gemeinsamem GND zum Arduino) versorgt.

## 3. Workspace-Struktur & Python-Bibliothek

Das Projekt folgt strikt dem *Separation of Concerns*-Prinzip. Die Logik ist in eine modulare Bibliothek (`cps_lib`) ausgelagert.

Plaintext

```
/workspace
 ├── configs/
 │    └── medication_plans.json   # Lokale, dynamische Datenbank der Pläne
 ├── cps_lib/
 │    ├── __init__.py             # Macht den Ordner zum Python-Modul
 │    ├── demo.py                 # Die lineare Ausgabe-Pipeline (Pitch-Sequenz)
 │    ├── normal_mode.py          # Hintergrund-Scheduler, JSON-Parser & RFID-Abfrage
 │    ├── oled.py                 # Threading-basiertes Luma.oled Display-Rendering
 │    ├── serial_link.py          # Stabile serielle Kommunikation mit 60s Timeout
 │    ├── servomotor.py           # Abstraktionsschicht für Winkel-Befehle
 │    ├── steppermotor.py         # Hardware-Muster (z.B. Radar-Sweep, 180°-Drehung)
 │    └── ultraschall.py          # Distanzberechnung
 ├── cps_bridge.ino               # Der C++ Code für den Arduino
 └── main.py                      # Einstiegspunkt (CLI) und Thread-Management
```

## 4. System-Flow: Wie funktioniert es?

1. **Planung (Web -> JSON):** Über ein externes Interface werden Zeiten und Dosen in der Datei `medication_plans.json` gespeichert. Dies passiert rein lokal (DSGVO-konform).
2. **Live-Scheduling:** Die Datei `normal_mode.py` läuft als Hintergrund-Thread auf dem Pi. Sie liest minütlich die JSON-Datei ein. Stimmen Wochentag und Uhrzeit überein, wird die Ausgabelogik (`demo.py`) getriggert.
3. **Vorbereitung (Asynchron):** Das OLED-Display wechselt in den Ladebalken-Modus. Der Stepper-Motor rüttelt die Pillen in den internen Schacht. Zu diesem Zeitpunkt ist das Gerät nach außen noch verschlossen.
4. **Ausgabe (Fail-Safe):** Das System wartet in einer Schleife, bis der Ultraschallsensor eine Distanz von <= 10 cm meldet (Hand des Patienten). Erst dann sendet der Pi den Befehl `SRV:180` an den Arduino, der den Servo öffnet und die Pillen freigibt.
5. **Sicherheit (RFID):** Parallel fragt der Pi dauerhaft `RFID:GET` ab. Wird der Chip einer Pflegekraft erkannt, öffnet Servo 2 kurzzeitig das obere Nachfüll-Schloss.

## 5. Größte technische Hürden & unsere Lösungen

Während der Entwicklung stießen wir auf klassische Herausforderungen der Embedded-Entwicklung. So wurden sie gelöst:

### Hürde 1: Arduino RAM-Overflow (Speichermangel)

- **Problem:** Das OLED-Display benötigte zusammen mit der Bibliothek `U8g2` zu viel des extrem knappen SRAMs (2 KB) des Arduinos. Der Arduino stürzte unvorhersehbar ab.
- **Lösung:** **Architektur-Wechsel.** Das Display wurde physisch vom Arduino an den Raspberry Pi (I2C) ausgelagert. Rendering und Fonts werden nun über Python (`luma.oled` & `Pillow`) berechnet. Der Arduino wurde zur reinen, ausfallsicheren Sensor-Bridge "degradiert" und hat nun 90 % Speicher frei.

### Hürde 2: Stepper-Motor zu schwach / verliert Schritte

- **Problem:** Der kleine 28BYJ-48 Stepper hatte im Half-Step-Modus nicht genug Drehmoment für mechanische Widerstände und "rutschte" durch (Skipping). Bei Sweeps drehte er sich mit der Zeit endlos weiter ("Massenträgheits-Drift").
- **Lösung:** Umprogrammierung des Arduinos auf den **Dual-Coil Full-Step Mode (Power-Modus)**. Es stehen nun immer zwei Spulen gleichzeitig unter Strom für maximales Drehmoment. Zusätzlich wurde die Geschwindigkeit (`delayMicroseconds(3000)`) gesenkt, um das Magnetfeld voll aufzubauen, und ein kurzes `time.sleep(0.3)` in der Python-Muster-Logik integriert, um den Schwung vor einem Richtungswechsel abzubremsen.

### Hürde 3: SPI-Pin Konflikt

- **Problem:** Der MFRC522 RFID-Reader benötigt hardwareseitig zwingend die SPI-Pins 11, 12 und 13. Diese waren bereits durch den Stepper belegt.
- **Lösung:** Digitale Flexibilität genutzt. Der Stepper wurde auf die Analog-Pins (A0–A3) des Arduinos umverkabelt. Ein Arduino kann Analog-Pins problemlos als digitale Ausgänge (`OUTPUT`) deklarieren und nutzen, wodurch der SPI-Bus für das RFID-Modul frei wurde.

### Hürde 4: Brownout durch Servos (System-Abstürze)

- **Problem:** Wenn die RFID-Karte erkannt wurde, sollte der Servo anlaufen. Das System fror jedoch sofort ein.
- **Ursache:** Servos ziehen beim Anlaufen sehr hohe Stromspitzen (Inrush Current). Der 5V-Regler des Arduinos konnte das nicht leisten. Die Spannung brach ein (Brownout), was sofort den 3.3V-gespeisten RFID-Chip und den Arduino einfrieren ließ.
- **Lösung:** Hardware-Entkopplung. Versorgung stromhungriger Aktoren (Servos/Stepper) über separate Stromquellen (mit Ground-Sharing) oder Puffer-Kondensatoren, um Logik-Strom (Arduino/Sensoren) von Antriebs-Strom zu trennen.

### Hürde 5: Befehls-Staus & Serial Timeout

- **Problem:** Bei längeren Stepper-Mustern (die > 10 Sekunden dauern), warf Python Fehler oder fing an, Befehle wirr zwischenzuspeichern, weil der Arduino scheinbar nicht mehr reagierte.
- **Lösung:** Anpassung der seriellen Kommunikation. Das Timeout in der `serial_link.py` wurde auf 60 Sekunden erhöht. Die Python-Bridge blockiert nun absichtlich synchron, bis der Arduino mit `ACK:STP`die physische Beendigung der Bewegung bestätigt. Systemzustände bleiben so strikt synchron.
