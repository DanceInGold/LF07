# MHTF – Medical & Health Tracking Framework

## Projektbeschreibung

Das Medical & Health Tracking Framework (MHTF) ist ein im Rahmen des Lernfeldes 07 entwickeltes IoT- und Datenbankprojekt zur digitalen Verwaltung und Überwachung von Medikamentenplänen sowie zur RFID-basierten Authentifizierung von Benutzern.

Ziel des Projekts ist die Entwicklung eines Systems, das eine zentrale Verwaltung medizinischer Daten ermöglicht und gleichzeitig den Zugriff auf Funktionen und Informationen durch RFID-Karten absichert. Dabei werden verschiedene Hard- und Softwarekomponenten miteinander verbunden, um einen praxisnahen Anwendungsfall für Datenbanken, Embedded Systems, Webentwicklung und Hardwareintegration umzusetzen.

Das System besteht aus drei Hauptkomponenten:

### Raspberry Pi Zero W 1.1

Der Raspberry Pi Zero fungiert als Web- und Anwendungsserver. Darauf läuft eine Flask-Webanwendung, über die Benutzer Medikationspläne verwalten, RFID-Karten anlegen und Systemereignisse einsehen können.

Folgende Funktionen werden bereitgestellt:

- Benutzeranmeldung
- Verwaltung von Medikationsplänen
- Verwaltung von RFID-Karten
- Ereignisanzeige und Protokollierung
- MQTT-Kommunikation
- Verbindung zur MariaDB-Datenbank

Die Weboberfläche wurde mit Flask, HTML und CSS umgesetzt.

---

### Raspberry Pi 3

Der Raspberry Pi 3 übernimmt die Aufgaben als Datenbank- und Steuerzentrale.

Auf diesem Gerät laufen:

- MariaDB-Datenbank
- RFID-Reader-Dienst
- Kommunikation zwischen Arduino und Datenbank
- Speicherung von RFID-Ereignissen

Der RFID-Dienst empfängt die UID einer gescannten RFID-Karte vom Arduino und überprüft diese gegen die Datenbank.

Anschließend wird das Ergebnis an den Arduino zurückgesendet:

- ALLOW
- DENY

Zusätzlich wird jeder Scan in der Tabelle `event_logs` protokolliert.

---

### Arduino Uno

Der Arduino Uno ist für die direkte Hardwaresteuerung zuständig.

Folgende Komponenten sind angeschlossen:

- MFRC522 RFID-Leser
- LCD1602 I2C Display
- Buzzer

Der Arduino liest RFID-Karten aus und sendet die UID über die serielle Schnittstelle an den Raspberry Pi 3.

Anschließend wartet der Arduino auf die Antwort des Datenbankdienstes.

Je nach Ergebnis wird:

- „ERLAUBT“ auf dem Display angezeigt
- „VERWEIGERT“ auf dem Display angezeigt
- ein entsprechender Ton über den Buzzer ausgegeben

Dadurch liegt die eigentliche Berechtigungsprüfung vollständig in der Datenbank.

---

## Verwendete Technologien

### Software

- Python
- Flask
- SQLAlchemy
- MariaDB
- MQTT
- HTML
- CSS
- Arduino C++

### Hardware

- Raspberry Pi Zero W 1.1
- Raspberry Pi 3
- Arduino Uno
- MFRC522 RFID Reader
- LCD1602 I2C Display
- Buzzer

---

## Datenbankstruktur

Die Datenbank basiert auf MariaDB und enthält vier zentrale Tabellen.

### users

Verwaltung der Benutzerkonten.

Speichert:

- Benutzername
- Passwort-Hash
- Rolle
- Sprache
- Aktivstatus

### medication_plans

Verwaltung der Medikationspläne.

Speichert:

- Patientenname
- Medikament
- Stärke
- Dosierung
- Einnahmezeit
- Wochentage
- Medikamentenbestand

### rfid_cards

Verwaltung aller RFID-Karten.

Speichert:

- UID
- Bezeichnung
- Person
- Aktivstatus

### event_logs

Protokollierung aller relevanten Systemereignisse.

Speichert:

- RFID-Scans
- Logins
- Änderungen an Medikationsplänen
- Änderungen an RFID-Karten

---

## Systemablauf

1. Ein Benutzer legt eine RFID-Karte über die Weboberfläche an.
2. Die Karte wird in der Datenbank gespeichert.
3. Eine RFID-Karte wird am Arduino gescannt.
4. Der Arduino sendet die UID an den Raspberry Pi 3.
5. Der Raspberry Pi prüft die UID in der Tabelle `rfid_cards`.
6. Das Ergebnis wird als ALLOW oder DENY zurückgesendet.
7. Der Arduino zeigt das Ergebnis auf dem LCD an.
8. Der Buzzer gibt eine entsprechende Rückmeldung.
9. Das Ereignis wird in `event_logs` gespeichert.
10. Die Weboberfläche zeigt den Eintrag in den Logs an.

---

## Ziel des Projekts

Das Projekt verbindet mehrere Themengebiete des Lernfeldes:

- Datenbanken
- Webentwicklung
- Hardwareprogrammierung
- Netzwerkkommunikation
- Embedded Systems
- IoT-Anwendungen

Durch die Kombination von Flask, MariaDB, Arduino und RFID-Technologie entsteht ein vollständiges System zur Verwaltung und Überwachung medizinischer Informationen mit zentraler Authentifizierung über RFID-Karten.
