import serial
import time
import threading

SERIAL_PORT = '/dev/ttyACM0' 
BAUD_RATE = 9600

# Trage hier deine UID ein!
AUTHORIZED_UIDS = ["UID:D366A70D"] 

MIN_OPEN_TIME = 5.0
AUTO_CLOSE_TIME = 300.0 # 5 Minuten (300 Sekunden)

is_dispenser_open = False
time_opened = 0.0
countdown_thread = None
stop_event = threading.Event()
ser = None

def send_to_display(text):
    if ser:
        try:
            # Wir nutzen das Pipe-Symbol '|' als Zeilenumbruch für den Arduino
            formatted_text = text.replace('\n', '|')
            ser.write(f"{formatted_text}\n".encode('utf-8'))
        except Exception as e:
            print(f"Fehler beim Senden: {e}")

def countdown_task():
    """Läuft im Hintergrund und aktualisiert jede Sekunde das Display."""
    global is_dispenser_open
    
    end_time = time.time() + AUTO_CLOSE_TIME
    
    while not stop_event.is_set():
        remaining = end_time - time.time()
        
        if remaining <= 0:
            print("Auto-Close Timer abgelaufen.")
            close_dispenser(reason="Timeout")
            break
            
        # Formatieren als mm:ss
        mins, secs = divmod(int(remaining), 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        # Sende "Unlocked" und den Timer (durch | getrennt)
        send_to_display(f"Dispenser Unlocked\nSchliesst in: {time_str}")
        
        # 1 Sekunde warten, aber auf das Stop-Event reagieren können
        stop_event.wait(1.0)

def close_dispenser(reason="Manuell"):
    global is_dispenser_open, countdown_thread
    
    if not is_dispenser_open:
        return

    is_dispenser_open = False
    print(f"Dispenser geschlossen ({reason}).")
    
    # Countdown-Thread sauber beenden
    stop_event.set()
    if countdown_thread:
        countdown_thread.join(timeout=1.0)
    
    # Motor/Servo-Logik hier einfügen
    
    send_to_display("Dispenser Locked\nSystem Bereit")

def open_dispenser():
    global is_dispenser_open, time_opened, countdown_thread
    
    is_dispenser_open = True
    time_opened = time.time()
    print("Dispenser geöffnet.")
    
    # Motor/Servo-Logik hier einfügen
    
    # Alten Thread beenden, falls einer läuft
    stop_event.set()
    if countdown_thread:
        countdown_thread.join(timeout=1.0)
        
    # Neuen Countdown-Thread starten
    stop_event.clear()
    countdown_thread = threading.Thread(target=countdown_task)
    countdown_thread.daemon = True
    countdown_thread.start()
    
def main():
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"Verbunden an {SERIAL_PORT}")
        send_to_display("System Bereit")

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                
                if line.startswith("UID:"):
                    print(f"Gelesen: {line}")
                    
                    if line in AUTHORIZED_UIDS:
                        current_time = time.time()
                        
                        if not is_dispenser_open:
                            open_dispenser()
                        else:
                            time_since_open = current_time - time_opened
                            if time_since_open >= MIN_OPEN_TIME:
                                print(f"Chip erneut gelesen nach {time_since_open:.1f}s.")
                                close_dispenser()
                            else:
                                remaining = MIN_OPEN_TIME - time_since_open
                                print(f"Zu frueh. Warte noch {remaining:.1f}s.")
                                # Wir blockieren kurz den normalen Timer für diese Meldung
                                send_to_display(f"Mindestzeit!\nWarte {int(remaining)+1}s...")
                    else:
                        print("Unbekannter Chip!")
                        send_to_display("Zugriff\nverweigert!")
                        time.sleep(2)
                        if not is_dispenser_open:
                            send_to_display("System Bereit")

            time.sleep(0.1)

    except serial.SerialException as e:
        print(f"Serieller Fehler: {e}")
    except KeyboardInterrupt:
        print("\nBeenden...")
        stop_event.set()
    finally:
        if ser:
            ser.close()

if __name__ == '__main__':
    main()
