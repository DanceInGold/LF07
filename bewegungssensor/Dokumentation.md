# Sensor-Einheit für einen automatischen Medikamentenspender

## 1. Ziel des Projekts

Im Rahmen des Projekts wurde eine **Sensor-Einheit für einen automatischen Medikamentenspender** entwickelt.

Das Ziel der Sensorik ist es, eine Person zu erkennen, die sich dem Medikamentenspender nähert, und anschließend festzustellen, ob eine Hand für die Medikamentenentnahme in den vorgesehenen Bereich gehalten wird.

### Ablauf

```text
Person nähert sich
        ↓
PIR erkennt Bewegung
        ↓
PERSON_READY
        ↓
Hand wird in den Entnahmebereich gehalten
        ↓
Hand muss 2 Sekunden ununterbrochen dort bleiben
        ↓
HAND_DETECTED
        ↓
hand_ready = true
        ↓
READY_FOR_DISPENSING
        ↓
Sensor-Ablauf wird beendet
```

Dabei werden zwei verschiedene Sensoren eingesetzt:

- **HC-SR501 PIR Motion Sensor** – erkennt Bewegungen im Erfassungsbereich.
- **HC-SR04 Ultraschallsensor** – misst den Abstand zu einem Objekt, beispielsweise einer Hand, die sich dem Entnahmebereich nähert.

Die Sensordaten werden von einem **Arduino UNO R3** erfasst und anschließend über eine USB-Seriell-Verbindung an einen **Raspberry Pi** weitergegeben.

Der Raspberry Pi übernimmt die übergeordnete Steuerung des Systems. Die Sensorik liefert ihm Informationen darüber, ob eine Bewegung erkannt wurde und ob sich beispielsweise eine Hand im vorgesehenen Entnahmebereich befindet.

---

## 2. Verwendete Komponenten

| Komponente | Aufgabe |
|---|---|
| **Arduino UNO R3** | Sensoren auslesen, Sensordaten verarbeiten und Statusinformationen übertragen |
| **Raspberry Pi** | Übergeordnete Verarbeitung und Steuerung |
| **HC-SR501 PIR** | Bewegung erkennen |
| **HC-SR04 Ultraschallsensor** | Abstand im Entnahmebereich messen |
| **Breadboard** | Prototypischer Aufbau und Stromverteilung |
| **Jumper Wire** | Elektrische Verbindung der Komponenten |
| **USB-Kabel** | Kommunikation zwischen Arduino und Raspberry Pi |

---

## 3. Arduino UNO R3

Der **Arduino UNO R3** ist der Mikrocontroller der Sensor-Einheit.

Seine Aufgabe besteht darin, die angeschlossenen Sensoren direkt auszulesen und deren Zustände zu verarbeiten.

Der Arduino übernimmt dabei:

1. Initialisierung der Sensoren
2. Auslesen des PIR-Sensors
3. Erkennen einer Bewegung
4. Aktivieren der Handerkennung
5. Messen des Abstands mit dem HC-SR04
6. Überprüfen der 2-Sekunden-Bedingung
7. Setzen der Variable `hand_ready`
8. Übertragen der Statusinformationen über die serielle Schnittstelle

Der Arduino wurde verwendet, weil Sensoren wie der HC-SR501 und HC-SR04 direkt und unkompliziert über digitale Ein- und Ausgänge des Mikrocontrollers angeschlossen werden können.

---

## 4. Raspberry Pi

Der **Raspberry Pi** übernimmt die übergeordnete Kommunikation und Steuerung.

Der Arduino ist hauptsächlich für die **direkte Sensorverarbeitung** zuständig. Der Raspberry Pi kann anschließend die vom Arduino übertragenen Informationen für weitere Funktionen des Medikamentenspenders verwenden.

Die Verbindung zwischen beiden Geräten erfolgt über USB.

Auf dem Raspberry Pi wird eine serielle Schnittstelle angelegt, beispielsweise:

```text
/dev/ttyACM0
```

Über diese Schnittstelle werden die vom Arduino gesendeten Nachrichten empfangen.

---

## 5. HC-SR501 PIR Motion Sensor

Der **HC-SR501** ist ein PIR-Sensor (*Passive Infrared Sensor*).

Er erkennt Bewegungen anhand von Veränderungen der Infrarotstrahlung in seinem Erfassungsbereich.

In diesem Projekt wird der Sensor verwendet, um **Bewegungen zu erkennen**.

### Anschlüsse

| Anschluss | Funktion |
|---|---|
| **VCC** | Versorgungsspannung |
| **GND** | Masse |
| **OUT** | Digitales Ausgangssignal |

Der Ausgang des Sensors wird vom Arduino ausgelesen.

Wenn eine Bewegung erkannt wird, liefert der Sensor ein **HIGH-Signal**.

---

## 6. HC-SR04 Ultraschallsensor

Der **HC-SR04** ist ein Ultraschallsensor zur Abstandsmessung.

Er sendet einen kurzen Ultraschallimpuls aus und misst anschließend die Zeit, bis das Echo zurückkommt.

Aus dieser Zeit kann der Abstand zu einem Objekt berechnet werden.

### Anschlüsse

| Anschluss | Funktion |
|---|---|
| **VCC** | 5-V-Versorgung |
| **GND** | Masse |
| **TRIG** | Start der Messung |
| **ECHO** | Empfang des Echos |

In diesem Projekt wird der HC-SR04 verwendet, um festzustellen, ob sich beispielsweise eine **Hand in einem bestimmten Abstand zum Medikamentenspender** befindet.

Als Beispiel wurde ein Grenzwert von **10 cm** verwendet.

---

## 7. Elektrische Verbindung

Die verwendeten Pins des Arduino UNO R3 sind:

| Komponente | Anschluss | Arduino |
|---|---|---|
| **HC-SR04** | VCC | 5 V |
| **HC-SR04** | GND | GND |
| **HC-SR04** | TRIG | D7 |
| **HC-SR04** | ECHO | D8 |
| **HC-SR501** | VCC | 5 V |
| **HC-SR501** | GND | GND |
| **HC-SR501** | OUT | D6 |

Die Kommunikation zwischen Arduino und Raspberry Pi erfolgt zusätzlich über USB.

---

## 8. Kommunikation zwischen Arduino und Raspberry Pi

| Komponente | Aufgabe |
|---|---|
| **Arduino UNO R3** | Sensoren auslesen und Daten übertragen |
| **Raspberry Pi** | Übergeordnete Verarbeitung und Steuerung |

Die vom Arduino erfassten Sensorinformationen werden über die USB-Seriell-Verbindung an den Raspberry Pi übertragen.

Beispielsweise kann der Arduino Statusinformationen wie:

```text
HAND_READY:1
```

an den Raspberry Pi senden.

---

# 9. Neue Sensorlogik nach der Anpassung

Die Logik wurde so angepasst, dass die Hand nicht nur kurz erkannt werden muss. Sie muss **mindestens 2 Sekunden ohne Unterbrechung** im vorgesehenen Bereich bleiben.

### Ablauf

1. Die Hand kommt in den Bereich (**< 10 cm**).
2. Ein Timer startet.
3. Die Hand muss **mindestens 2 Sekunden ohne Unterbrechung** im Bereich bleiben.
4. Nach Ablauf der 2 Sekunden wird:

```cpp
hand_ready = true;
```

5. Anschließend wird beispielsweise:

```text
HAND_READY:1
```

über die serielle Schnittstelle an den Raspberry Pi gesendet.
6. Das Arduino-Programm beendet die Messschleife.

---

## 10. Variable `hand_ready`

Die Variable `hand_ready` wird als **globale Variable** definiert, damit sie später auch von anderen Teilen des Programms verwendet werden kann.

### Initialisierung

```cpp
bool hand_ready = false;
```

Zu Beginn ist die Variable also `false`.

Sobald die Hand mindestens 2 Sekunden lang ununterbrochen erkannt wurde, wird sie auf `true` gesetzt:

```cpp
hand_ready = true;
```

### Funktion der Variable

```text
hand_ready = false
        ↓
Hand wird erkannt
        ↓
Timer startet
        ↓
Hand bleibt mindestens 2 Sekunden im Bereich
        ↓
hand_ready = true
        ↓
HAND_READY:1 wird über Serial gesendet
```

---

# 11. Gesamtablauf der Sensorik

Der vollständige Ablauf lässt sich wie folgt darstellen:

```text
1. PIR erkennt Person / Bewegung
              ↓
2. Person ist in der Nähe
              ↓
3. HC-SR04 wird aktiviert
              ↓
4. Hand wird in den Entnahmebereich gehalten
              ↓
5. Abstand < 10 cm?
              ↓
        ┌─────┴─────┐
        │           │
       Nein        Ja
        │           │
        │       Timer startet
        │           ↓
        │       Hand bleibt 2 Sekunden
        │       ununterbrochen im Bereich?
        │           ↓
        │      hand_ready = true
        │           ↓
        │      HAND_READY:1
        │           ↓
        └────→ READY_FOR_DISPENSING
                    ↓
              Sensor-Ablauf beendet
```

---

# 12. Arduino-Setup und Installation

## 12.1 Prüfen, ob der Arduino erkannt wird

Auf dem Raspberry Pi kann zunächst geprüft werden, ob der Arduino angeschlossen und erkannt wurde:

```bash
ls /dev/ttyACM*
```

Beispielausgabe:

```text
/dev/ttyACM0
```

---

## 12.2 Arduino CLI installieren und UNO-Unterstützung einrichten

Zunächst wird der Index der verfügbaren Arduino-Cores aktualisiert:

```bash
arduino-cli core update-index
```

Anschließend wird die Unterstützung für den klassischen Arduino UNO installiert:

```bash
arduino-cli core install arduino:avr
```

Der `arduino:avr`-Core enthält die Unterstützung für den klassischen UNO. Für den Arduino UNO R3 wird als FQBN verwendet:

```text
arduino:avr:uno
```

---

## 12.3 Arduino erkennen

Mit folgendem Befehl kann überprüft werden, ob der Arduino von der Arduino CLI erkannt wird:

```bash
arduino-cli board list
```

---

# 13. Projektverzeichnis erstellen

Ein Projektverzeichnis kann beispielsweise mit folgendem Befehl erstellt werden:

```bash
mkdir /dispenser_final/MoveSensor
```

Anschließend kann in das Verzeichnis gewechselt werden:

```bash
cd /dispenser_final/MoveSensor
```

---

# 14. Arduino-Datei erstellen

Die Arduino-Datei wird als `MoveSensor.ino` angelegt.

Beispielsweise kann dafür `nano` verwendet werden:

```bash
nano MoveSensor.ino
```

Anschließend wird der Arduino-Code eingegeben und gespeichert.

---

# 15. Arduino-Code kompilieren

Der Code wird mit folgendem Befehl kompiliert:

```bash
arduino-cli compile --fqbn arduino:avr:uno .
```

Wenn die Kompilierung erfolgreich abgeschlossen wurde, kann der Code auf den Arduino übertragen werden.

---

# 16. Code auf den Arduino laden

Zum Hochladen des Programms wird folgender Befehl verwendet:

```bash
arduino-cli upload -p /dev/ttyACM0 -b arduino:avr:uno .
```

Dabei bezeichnet:

- `/dev/ttyACM0` die serielle Schnittstelle des Arduino.
- `arduino:avr:uno` das verwendete Board.
- `.` das aktuelle Projektverzeichnis.

---

# 17. Sensorik testen

Nach dem Hochladen kann die serielle Ausgabe des Arduino über den Serial Monitor überprüft werden.

Dazu wird beispielsweise folgender Befehl verwendet:

```bash
arduino-cli monitor -p /dev/ttyACM0 --config baudrate=9600
```

Alternativ kann die Kommunikation über ein Python-Programm getestet werden:

```bash
python3 SensorReader.py
```

Der Arduino sendet seine Sensorinformationen über die USB-Seriell-Verbindung an den Raspberry Pi.

---

# 18. Zusammenfassung

Die entwickelte Sensor-Einheit übernimmt die Erkennung einer Person und die anschließende Erkennung einer Hand im Entnahmebereich.

Der **HC-SR501 PIR-Sensor** erkennt zunächst eine Bewegung bzw. eine Person in der Nähe des Medikamentenspenders.

Anschließend wird der **HC-SR04 Ultraschallsensor** für die Handerkennung verwendet. Befindet sich eine Hand in einem Abstand von weniger als **10 cm**, startet ein Timer.

Die Hand muss mindestens **2 Sekunden ohne Unterbrechung** in diesem Bereich bleiben. Erst danach wird:

```cpp
hand_ready = true;
```

gesetzt und beispielsweise folgende Nachricht über die serielle Schnittstelle an den Raspberry Pi übertragen:

```text
HAND_READY:1
```

Der Arduino übernimmt damit die direkte Sensorverarbeitung, während der Raspberry Pi die übergeordnete Steuerung des Medikamentenspenders übernehmen kann.
