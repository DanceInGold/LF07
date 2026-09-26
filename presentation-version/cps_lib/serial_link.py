import serial
import time
import threading

PORT = '/dev/ttyACM0' 
BAUDRATE = 115200

# Mutex-Lock für sichere Multithreading-Kommunikation
serial_lock = threading.Lock()

try:
    arduino = serial.Serial(PORT, BAUDRATE, timeout=2)
    time.sleep(2) 
except Exception as e:
    print(f"Fehler beim Öffnen des Ports {PORT}: {e}")
    arduino = None

def send_and_receive(cmd):
    """Sendet einen Befehl thread-sicher und wartet auf Antwort."""
    if arduino:
        with serial_lock: # Sperrt den Port für andere Threads
            arduino.write((cmd + '\n').encode('utf-8'))
            response = arduino.readline().decode('utf-8').strip()
            return response
    return None