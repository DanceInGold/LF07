# Projektdokumentation

# **Prototyp – Cyber-Physisches Zugangssystem**

## **1. Einleitung und Zielsetzung**

Im Rahmen dieses Teilprojekts wurde ein kleines cyber-physisches System entworfen und prototypisch umgesetzt. Das primäre Ziel war die Evaluierung und der Test einer stabilen, bidirektionalen seriellen Kommunikation zwischen einem Mikrocontroller (Arduino) und einem Single-Board-Computer (Raspberry Pi).

Dieses Setup dient als Proof of Concept für ein geplantes finales Projekt (z. B. einen automatisierten Dispenser). Dabei übernimmt der Arduino hardwarenahe Aufgaben (Sensorik/Aktorik) als "Dumb Node", während der Raspberry Pi (Headless) die zentrale Steuerlogik, Zeitsteuerung und Authentifizierung übernimmt.

## **2. Hardware-Architektur und Verkabelung**

Das System besteht aus drei Hauptkomponenten: Dem Arduino als I/O-Schnittstelle, einem MFRC522 RFID-Modul zur Authentifizierung und einem 1.3" OLED-Display (SH1106) zur visuellen Rückmeldung. Die Verbindung zum Raspberry Pi erfolgt über USB (Seriell).

**Verkabelungsplan (Arduino Uno / Nano):**

| **Komponente** | **Pin am Modul** | **Pin am Arduino** | **Protokoll / Anmerkung** |
| --- | --- | --- | --- |
| **RFID-Modul** | SDA (SS) | D10 | SPI (Chip Select) |
| **(MFRC522)** | SCK | D13 | SPI Clock |
|  | MOSI | D11 | SPI Data Out |
|  | MISO | D12 | SPI Data In |
|  | RST | D8 | Digital I/O (Reset) |
|  | 3.3V | 3.3V | **Kritisch:** Nur 3.3V nutzen! |
|  | GND | GND | Masse |
| **OLED-Display** | SDA | A4 | I2C Data |
| **(SH1106, 1.3")** | SCL | A5 | I2C Clock |
|  | VCC | 5V (oder 3.3V) | Versorgungsspannung |
|  | GND | GND | Masse |
| **Raspberry Pi** | USB-A Port | USB-Port | Strom & Serielle Daten (/dev/ttyACM0) |

## **3. Software-Architektur und Kommunikation**

Die Kommunikation zwischen den Geräten erfolgt über eine serielle USB-Verbindung mit einer Baudrate von 9600. Das Protokoll ist textbasiert (ASCII) und nutzt Zeilenumbrüche (\n) als Terminatoren.

- **Arduino -> Raspberry Pi:** Sendet bei Erkennung einer RFID-Karte die ausgelesene UID im Format UID:XXXXXXXX\n.
- **Raspberry Pi -> Arduino:** Sendet String-Nachrichten für das Display. Ein Pipe-Symbol (|) wird als Trennzeichen für Zeilenumbrüche auf dem OLED interpretiert (z. B. Dispenser Unlocked|Schliesst in: 04:59\n).

### **3.1 Setup der seriellen Kommunikation (Raspberry Pi)**

Damit der Raspberry Pi per Python auf den seriellen Bus zugreifen kann, muss die entsprechende Bibliothek installiert sein:

Bash

```bash
# System-Paketquellen aktualisieren

sudo apt update

# Python Paketmanager und pyserial installieren

sudo apt install python3-pip

pip3 install pyserial
```

Das Python-Skript (dispenser.py) nutzt die Bibliothek serial.Serial('/dev/ttyACM0', 9600) und einen separaten Thread (threading.Thread), um die Countdown-Logik asynchron zur seriellen Lese-Schleife auszuführen.

## **4. Headless Arduino-Entwicklung via CLI (Raspberry Pi)**

Da der Raspberry Pi ohne grafische Oberfläche (headless via SSH) betrieben wird, erfolgt die gesamte Entwicklung, Kompilierung und das Flashen des Arduinos über das arduino-cli Tool.

### **Schritt 1: Installation der Arduino CLI**

Herunterladen und systemweit im Verzeichnis /usr/local/bin installieren:

Bash

```bash
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sudo BINDIR=/usr/local/bin sh
```

### **Schritt 2: Board-Identifikation**

Auslesen des angeschlossenen Arduinos, um den Port und den Fully Qualified Board Name (FQBN) zu ermitteln:

Bash

```bash
arduino-cli board list
```

*Typisches Ergebnis: Port: /dev/ttyACM0, FQBN: arduino:avr:uno*

### **Schritt 3: Core und Bibliotheken installieren**

Damit der C++ Code für die AVR-Architektur übersetzt werden kann und die spezifische Hardware unterstützt wird, müssen der Core und die Bibliotheken geladen werden:

Bash

```bash
# Core-Index aktualisieren und AVR-Core installieren

arduino-cli core update-index

arduino-cli core install arduino:avr

# Benötigte Bibliotheken für RFID und OLED installieren

arduino-cli lib install "MFRC522" "Adafruit SH110X" "Adafruit GFX Library"
```

### **Schritt 4: Projekt erstellen und kompilieren**

Die Arduino CLI erwartet, dass der Ordnername und die .ino-Datei identisch benannt sind. In einem Projektordner darf sich immer nur eine Haupt-Ino-Datei befinden.

Bash

```bash
# 1. Projektordner erstellen

mkdir ~/dispenser_final

# 2. C++ Quellcode erstellen/bearbeiten (öffnet den nano Texteditor)

nano ~/dispenser_final/dispenser_final.ino

# (Code einfügen, Speichern mit Strg+O -> Enter -> Strg+X)

# 3. Sketch kompilieren (Prüft auf Syntaxfehler und baut das Binary)

arduino-cli compile --fqbn arduino:avr:uno ~/dispenser_final
```

### **Schritt 5: Upload auf den Arduino**

Nach erfolgreicher Kompilierung wird der Code auf den Mikrocontroller geflasht:

Bash

```bash
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno ~/dispenser_final
```

*Gibt das Terminal avrdude: done. Thank you. aus, war der Upload erfolgreich und der Arduino führt den Code sofort aus.*


# Fachwort-Kompendium:

## 1. Allgemeine System- und Hardwarebegriffe

- **Cyber-Physisches System (CPS):**
    
    Ein System, in dem Software-Komponenten (Cyber) mit mechanischen oder elektronischen Bauteilen (Physisch) direkt kommunizieren. In unserem Fall: Python-Code entscheidet logisch, ob ein physischer Dispenser (Hardware) geöffnet wird.
    
- **Proof of Concept (PoC):**
    
    Ein Machbarkeitsnachweis. Ein früher Prototyp, der nicht perfekt sein muss, aber beweist, dass die grundlegende Idee in der Praxis funktioniert (hier: Kommunikation zwischen Pi und Arduino).
    
- **Headless (Headless Mode):**
    
    "Ohne Kopf". Bedeutet, dass ein Computer (hier der Raspberry Pi) ohne Monitor, Tastatur oder Maus betrieben wird. Man steuert ihn ausschließlich über das Netzwerk (z. B. via SSH) von einem anderen Rechner aus.
    
- **CLI (Command Line Interface):**
    
    Die Kommandozeile (oder Konsole). Anstatt Fenster mit der Maus anzuklicken, steuert man den Computer ausschließlich durch die Eingabe von Textbefehlen.
    
- **Baudrate:**
    
    Die Geschwindigkeit der seriellen Datenübertragung zwischen zwei Geräten (hier USB zwischen Pi und Arduino). `9600` bedeutet, es werden 9600 Bits pro Sekunde übertragen. Sender und Empfänger müssen zwingend dieselbe Baudrate eingestellt haben.
    

## 2. Kommunikationsprotokolle & Arduino-Spezifika

- **I/O (Input / Output):**
    
    Ein- und Ausgabe. Bezeichnet die Pins am Arduino, an die man Bauteile anschließt. Ein Input liest Daten (z. B. Taster, Sensoren), ein Output gibt Strom aus (z. B. LEDs, Motoren).
    
- **I2C (Inter-Integrated Circuit):**
    
    Ein Bus-System zur Kommunikation zwischen Chips über kurze Distanzen (genutzt für unser OLED-Display). Der große Vorteil: Es benötigt immer nur genau 2 Datenkabel (SDA für Daten, SCL für den Takt), egal wie viele Geräte angeschlossen sind.
    
- **SPI (Serial Peripheral Interface):**
    
    Ein weiteres Bus-System (genutzt für unser RFID-Modul). Es ist deutlich schneller als I2C, benötigt aber in der Regel 4 Leitungen.
    
- **UID (Unique Identifier):**
    
    Die weltweit einmalige Seriennummer eines RFID-Chips. Anhand dieser Nummer erkennt unser Python-Skript, ob der Chip berechtigt ist.
    
- **FQBN (Fully Qualified Board Name):**
    
    Die genaue Bezeichnung des Arduino-Modells in der Kommandozeile (z. B. `arduino:avr:uno`). Das ist wichtig, da unterschiedliche Arduino-Boards verschiedene Mikrochips haben und der Code passend für den jeweiligen Chip übersetzt werden muss.
    

## 3. Die wichtigsten Linux/Bash-Befehle (Das "Handwerkszeug")

Diese Befehle tippt man in das CLI (Terminal) des Raspberry Pi ein, um das System zu steuern:

| **Befehl** | **Ausgeschrieben** | **Was er macht (Erklärung für das Team)** |
| --- | --- | --- |
| `mkdir` | **m**a**k**e **dir**ectory | Erstellt einen neuen, leeren Ordner (Verzeichnis). *Beispiel: `mkdir ~/dispenser`* |
| `cd` | **c**hange **d**irectory | Wechselt in einen anderen Ordner, ähnlich wie ein Doppelklick auf einen Ordner in Windows. *Beispiel: `cd ~/dispenser`* |
| `nano` | (Name des Editors) | Öffnet einen sehr einfachen Texteditor direkt im Terminal. Hier schreiben wir unseren Code. *Speichern mit `Strg+O`, Beenden mit `Strg+X`.* |
| `rm` | **r**e**m**ove | Löscht eine Datei dauerhaft (ohne Papierkorb!). *Beispiel: `rm alter_code.ino`* |
| `cp` | **c**o**p**y | Kopiert eine Datei von Ort A nach Ort B. |
| `mv` | **m**o**v**e | Verschiebt eine Datei. Wird unter Linux auch dazu genutzt, um Dateien einfach umzubenennen. |
| `sudo` | **s**uper**u**ser **do** | Führt den nachfolgenden Befehl mit Administratorrechten ("Chef-Rechten") aus. Wird oft für Installationen benötigt. |
| `apt` | **a**dvanced **p**ackage **t**ool | Der "App Store" von Linux (Debian/Ubuntu). Mit `sudo apt install <programm>` lädt und installiert man neue Software aus dem Internet. |
| `pip` / `pip3` | **p**ip **i**nstalls **p**ackages | Der "App Store" speziell für die Programmiersprache Python. Wir haben damit `pyserial` installiert. |
| `curl` | **c**lient **URL** | Lädt Daten (z. B. Installationsskripte) über einen direkten Link aus dem Internet herunter und gibt sie im Terminal aus. |

## 4. Die Arduino CLI-Befehle verstehen

Wenn wir mit der `arduino-cli` arbeiten, machen wir im Grunde das, was der große, runde "Pfeil-Button" in der normalen grafischen Arduino-Software macht, nur eben manuell in zwei Schritten:

1. **`arduino-cli compile ...` (Kompilieren):**
    
    Computer verstehen kein C++. Dieser Befehl nimmt unseren für Menschen lesbaren Text-Code und übersetzt ihn ("kompiliert" ihn) in eine binäre Maschinensprache, die der kleine Chip auf dem Arduino versteht. Zudem wird hier geprüft, ob wir Tippfehler oder fehlende Semikolons im Code haben.
    
2. **`arduino-cli upload ...` (Hochladen):**
    
    Nimmt die im vorherigen Schritt erstellte Maschinensprache und schiebt sie über das USB-Kabel (z. B. über den Port `/dev/ttyACM0`) direkt in den Speicher des Arduinos.