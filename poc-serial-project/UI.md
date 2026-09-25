# UI & Interaktion – Prototyp

## 1. Aufgabenbereich und Zielsetzung

Mein Aufgabenbereich umfasst die Benutzeroberfläche und das Feedback des Dispensers.

Dazu gehören:

- Erkennung einer RFID-Karte als Auslöser
- Anzeige von Informationen über das OLED-Display
- Anzeige von „ZUGRIFF ERLAUBT“ bzw. „ZUGRIFF VERWEIGERT“
- Visuelles Feedback über eine grüne bzw. rote LED
- Akustisches Feedback über einen Buzzer
- Automatisches Ausblenden der Anzeige nach 5 Sekunden
- Vorbereitung der späteren Anzeige der nächsten Dosis

Der aktuelle Stand stellt einen funktionierenden UI-Prototyp dar. Die tatsächlichen Berechtigungen und Dosierungsinformationen sollen später mit der Logik bzw. Datenbank des Gesamtsystems verbunden werden.

## 2. Hardware und Verkabelung

Für die UI wurden folgende Komponenten verwendet:

| Komponente | Arduino-Anschluss |
|---|---|
| RC522 SDA/SS | D10 |
| RC522 SCK | D13 |
| RC522 MOSI | D11 |
| RC522 MISO | D12 |
| RC522 RST | D9 |
| RC522 3.3V | 3.3V |
| RC522 GND | GND |
| OLED SDA | A4 |
| OLED SCL | A5 |
| OLED VDD | 5V |
| OLED GND | GND |
| Grüne LED | D6 |
| Rote LED | D7 |
| Buzzer | D8 |

Der Arduino ist über USB mit dem Raspberry Pi verbunden.

Verwendeter serieller Port:

```text
/dev/ttyACM0
```

## 3. Funktionsweise der UI

Die RFID-Karte dient als Auslöser für die Benutzeroberfläche.

Nach dem Erkennen einer Karte wird die UID ausgelesen und mit einer hinterlegten Test-UID verglichen.

### Zugriff erlaubt

Bei einer autorisierten UID:

- OLED zeigt „ZUGRIFF ERLAUBT“
- grüne LED leuchtet
- ein positiver Signalton wird ausgegeben
- zusätzlich wird „Nächste Dosis“ als Platzhalter angezeigt

### Zugriff verweigert

Bei einer nicht autorisierten UID:

- OLED zeigt „ZUGRIFF VERWEIGERT“
- rote LED leuchtet
- es werden zwei tiefere Signaltöne ausgegeben

Die Berechtigungsprüfung mit einer fest hinterlegten UID dient aktuell nur als Prototyp. Im späteren Gesamtsystem soll die Berechtigung über die zentrale Logik bzw. Datenbank erfolgen.

## 4. Automatisches Zurücksetzen

Nach der Anzeige bleibt das Feedback für 5 Sekunden sichtbar.

Danach werden:

- OLED-Anzeige gelöscht
- grüne LED ausgeschaltet
- rote LED ausgeschaltet
- Buzzer ausgeschaltet

Anschließend wartet das System wieder auf die nächste RFID-Karte.

## 5. Kompilieren und Upload

Das Projekt kann über die Arduino CLI kompiliert werden:

```bash
arduino-cli compile --fqbn arduino:avr:uno ~/dispenser_ui/rfid_oled_test
```

Anschließend wird der Sketch auf den Arduino übertragen:

```bash
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno ~/dispenser_ui/rfid_oled_test
```

Der aktuelle UI-Sketch befindet sich unter:

```text
~/dispenser_ui/rfid_oled_test/rfid_oled_test.ino
```

## 6. Ergebnis

Der UI-Prototyp ermöglicht damit eine vollständige Rückmeldung an den Benutzer:

**RFID-Karte → Prüfung → OLED + LED + Buzzer → 5 Sekunden Anzeige → Zurücksetzen**

Die Anzeige „Nächste Dosis“ ist momentan noch ein Platzhalter und kann später durch die tatsächlichen Daten aus der Datenbank ersetzt werden.
