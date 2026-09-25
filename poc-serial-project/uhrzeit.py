import serial
import time
from datetime import datetime

arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

time.sleep(2)

wochentage = {
    "Monday": "Montag",
    "Tuesday": "Dienstag",
    "Wednesday": "Mittwoch",
    "Thursday": "Donnerstag",
    "Friday": "Freitag",
    "Saturday": "Samstag",
    "Sunday": "Sonntag"
}

while True:

    jetzt = datetime.now()

    uhrzeit = jetzt.strftime("%H:%M")
    datum = jetzt.strftime("%d.%m.%Y")

    wochentag = wochentage[jetzt.strftime("%A")]

    nachricht = f"TIME|{wochentag}|{uhrzeit}|{datum}\n"

    arduino.write(nachricht.encode())

    time.sleep(10)
