import serial
import time

PORT = "/dev/ttyACM0"
BAUDRATE = 9600

arduino = serial.Serial(
    PORT,
    BAUDRATE,
    timeout=1
)

time.sleep(2)

print("Warte auf Sensor-System...")

try:
    while True:

        if arduino.in_waiting > 0:

            message = arduino.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if message:
                print(message)

            if message == "READY_FOR_DISPENSING":
                print("System bereit - Programm wird beendet.")
                break

finally:
    arduino.close()

print("Sensor-System beendet.")