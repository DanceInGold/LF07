# Docu: Demo Cyber-Physical System (CPS) Prototyp

## 1. Projektübersicht & Architektur

Dieses Projekt implementiert einen Cyber-Physical System (CPS) Prototypen mit einer strikten Trennung von Logik und Hardware-Ausführung.

- **Logik-Ebene (Raspberry Pi):** Ein modulares Python-Backend übernimmt die komplette Entscheidungsfindung, Zeitsteuerung (Multithreading) und Ablauflogik.
- **Hardware-Ebene (Arduino):** Agiert als "Dumb Bridge". Er empfängt strukturierte String-Befehle über die serielle USB-Schnittstelle, steuert die Aktoren an, liest Sensordaten aus und sendet die Ergebnisse zurück.

Diese Architektur ermöglicht es, komplexe Berechnungen auf dem leistungsstärkeren Raspberry Pi auszuführen, während der Arduino die harten Echtzeitanforderungen der Hardware-Pins übernimmt.

## 2. Systemanforderungen (Requirements)

### 2.1 Hardware-Anforderungen

- **Controller:**
    - Raspberry Pi (mit USB-Port für serielle Kommunikation)
    - Arduino (Uno, Nano oder Mega)
- **Aktoren:**
    - Schrittmotor: 28BYJ-48 inkl. ULN2003 Treiberboard
    - Servomotor: SG90
- **Sensoren & Ausgabe:**
    - Ultraschallsensor: HC-SR04
    - OLED Display: 1.3" I2C SH1106 (128x64 Pixel)
- **Sonstiges:** USB-Kabel (Pi zu Arduino), Jumper-Kabel (Breadboard). *Hinweis: Für einen stabilen Betrieb sollten Stepper und Servo idealerweise über eine separate 5V-Stromquelle (mit gemeinsamem Ground zum Arduino) versorgt werden.*

### 2.2 Software-Anforderungen

- **Raspberry Pi:** Python 3.x, Bibliothek `pyserial`
- **Arduino IDE:** Für den Upload des Bridge-Skripts
- **Arduino Bibliotheken:** `Servo` (Standard), `Stepper` (Standard), `U8g2` (von *oliver*, für das SH1106 Display)

## 3. Pin-Layout & Verkabelung (Arduino)

Die Hardware wird wie folgt an den Arduino angeschlossen. Die I2C-Pins variieren je nach Arduino-Modell (beim Uno/Nano sind es A4 und A5).

| **Komponente** | **Pin am Arduino** | **Bemerkung** |
| --- | --- | --- |
| **Servo (SG90)** | `D3` (PWM) | Steuerleitung (meist orange/gelb) |
| **HC-SR04 (Ultraschall)** | `D4` | TRIG (Trigger) |
|  | `D5` | ECHO |
| **28BYJ-48 (Stepper via ULN2003)** | `D8` | IN1 |
|  | `D10` | IN2 *(Gekreuzt für flüssigen Lauf)* |
|  | `D9` | IN3 *(Gekreuzt für flüssigen Lauf)* |
|  | `D11` | IN4 |
| **SH1106 OLED Display (I2C)** | `A4` | SDA (Data) |
|  | `A5` | SCL (Clock) |

## 4. Software-Struktur (Raspberry Pi)

Das Python-Projekt ist modular in einer eigenen Bibliothek (`cps_lib`) aufgebaut:

```
cps_projekt/
├── cps_bridge.ino           # Arduino C++ Code
├── main.py                  # Interaktives Steuerungs-Terminal (CLI)
├── presentation_demo.py     # Skript für die automatisierte Präsentation
└── cps_lib/
    ├── __init__.py
    ├── serial_link.py       # Thread-sicheres Kommunikationsmodul (UART)
    ├── steppermotor.py      # Abstrakte Bewegungsmuster (Radar, 180°-Drehung)
    ├── servomotor.py        # Winkeleinstellung (0-180°)
    ├── ultraschall.py       # Distanzmessung und Parsing
    └── oled.py              # Hintergrund-Thread für Timer & Systemuhrzeit
```

## 5. Inbetriebnahme (How to Use)

### Schritt 1: Arduino vorbereiten

1. Öffne die Arduino IDE.
2. Navigiere zu *Sketch -> Bibliothek einbinden -> Bibliotheken verwalten*. Suche nach **U8g2** und installiere die Bibliothek.
3. Verbinde den Arduino mit deinem Rechner.
4. Lade den Code aus der Datei `cps_bridge.ino` auf den Arduino hoch.
5. Verbinde den Arduino nun per USB mit dem Raspberry Pi.

### Schritt 2: Raspberry Pi vorbereiten

1. Klone oder kopiere die gesamte Ordnerstruktur (`cps_projekt/`) auf den Raspberry Pi.
2. Öffne ein Terminal und installiere die benötigte serielle Bibliothek
    
    Bash
    
    ```
    pip install pyserial
    ```
    
3. Prüfe in der Datei `cps_lib/serial_link.py`, ob der `PORT` korrekt ist (Standardmäßig `/dev/ttyACM0` oder `/dev/ttyUSB0`).

### Schritt 3: Ausführung der Skripte

Navigiere im Terminal in den Projektordner. Du hast nun zwei Möglichkeiten das System zu nutzen:

**Variante A: Interaktiver Modus**

Ideal zum Testen einzelner Komponenten und für manuelle Eingriffe.

Bash

```
python main.py
```

- Tippe `auto on`, um die Ultraschall-Logik im Hintergrund zu aktivieren.
- Tippe `srv 90`, um den Servo manuell zu steuern.
- Tippe `exit`, um das System sicher herunterzufahren.

**Variante B: Präsentationsmodus**

Führt den vordefinierten Ablauf für Demonstrationszwecke durch.

Bash

```
python presentation_demo.py
```

*Ablauf der Präsentation:*

1. Startet das OLED Display mit einem 120-Sekunden Timer.
2. Wartet im Hintergrund, bis der Timer abgelaufen ist.
3. Führt das Radar-Muster (120° Sweep) des Steppers aus.
4. Führt die 180° Drehung (mit 5s Pause) des Steppers aus.
5. Das System pausiert und wartet, bis du ein Objekt näher als 10 cm an den Ultraschallsensor hältst.
6. Der Servomotor schlägt auf 180° aus, um die Reaktionskette abzuschließen.