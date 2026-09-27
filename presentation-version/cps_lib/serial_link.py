import serial
import serial.tools.list_ports
import time
import threading

BAUDRATE = 115200
serial_lock = threading.Lock()
arduino = None

def find_arduino_port():
    """Sucht automatisch nach dem angeschlossenen Arduino."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Sucht nach gängigen Bezeichnungen für Arduinos/Serielle Chips auf Linux/Mac/Windows
        if "Arduino" in port.description or "ACM" in port.device or "USB" in port.device or "CH340" in port.description or "cu.usb" in port.device:
            return port.device
    return None

# Automatische Port-Erkennung
PORT = find_arduino_port()

if PORT:
    print(f"[Serial] Möglicher Arduino gefunden an Port: {PORT}")
    try:
        # Timeout auf 2s, damit sich das Programm nicht aufhängt, falls der Arduino nicht antwortet
        arduino = serial.Serial(PORT, BAUDRATE, timeout=10)
        time.sleep(5) # WICHTIG: Arduino startet neu, wenn der Port geöffnet wird
        print("[Serial] Verbindung erfolgreich hergestellt!")
    except Exception as e:
        print(f"[Serial] FEHLER: Port {PORT} konnte nicht geöffnet werden. (Rechte-Problem?)")
        print(f"Details: {e}")
        arduino = None
else:
    print("[Serial] FEHLER: Kein Arduino gefunden! Bitte USB-Verbindung prüfen.")

def send_and_receive(cmd):
    """Sendet einen Befehl thread-sicher und wartet auf Antwort."""
    if arduino:
        try:
            with serial_lock: 
                # Debug-Print: Zeigt dir im Terminal, was gerade gesendet wird
                # print(f"-> Sende: {cmd}") 
                
                arduino.write((cmd + '\n').encode('utf-8'))
                response = arduino.readline().decode('utf-8').strip()
                
                # Debug-Print: Zeigt dir die Antwort vom Arduino
                # print(f"<- Empfangen: {response}") 
                return response
        except Exception as e:
            print(f"[Serial] Verbindungsabbruch während der Übertragung: {e}")
            return None
    return None