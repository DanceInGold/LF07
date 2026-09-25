# MHTF - Medical & Health Tracking Framework

## Projektbeschreibung

MHTF ist ein Berufsschulprojekt zur Verwaltung von Medikationsplänen und RFID-basierten Berechtigungen.

## Hardware

- Raspberry Pi Zero W 1.1
- Raspberry Pi 3
- Arduino Uno
- MFRC522 RFID Reader
- LCD1602 I2C Display
- Buzzer

## Software

- Python
- Flask
- MariaDB
- SQLAlchemy
- MQTT
- Arduino C++

## Funktionen

- Benutzerverwaltung
- Medikationspläne
- RFID-Kartenverwaltung
- Datenbankgestützte RFID-Prüfung
- LCD-Anzeige
- Buzzer-Rückmeldung
- Event-Logging

## Architektur

RFID Karte
→ Arduino Uno
→ Raspberry Pi 3
→ MariaDB

Ergebnis:
- ALLOW
- DENY

→ LCD-Anzeige
→ Buzzer
→ event_logs
