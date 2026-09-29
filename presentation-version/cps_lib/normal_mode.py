import time
import threading
from cps_lib import servomotor, ultraschall
from cps_lib.serial_link import send_and_receive

# --- RFID KONFIGURATION ---
AUTHORIZED_UIDS = ["046F9A2A", "B348D911"]

is_running = False
is_active = False

def unlock_refill_station():
    """Öffnet das Schloss asynchron für 5 Sekunden."""
    print("\n[RFID] Autorisierung erfolgreich! Öffne Nachfüll-Schloss...")
    send_and_receive("SRV2:180")
    time.sleep(5)
    send_and_receive("SRV2:0")
    print("\n[RFID] Nachfüll-Schloss wieder verriegelt.")
    print("Eingabe > ", end="", flush=True)

def _auto_worker():
    global is_active, is_running
    while is_running:
        if is_active:
            # 1. Ultraschall-Abfrage
            dist = ultraschall.get_distance()
            if dist is not None and 0 < dist < 15.0:
                print(f"\n[Auto] Hand erkannt ({dist:.1f}cm)! Gebe Pillen aus.")
                servomotor.set_angle(180)
                time.sleep(2)
                servomotor.set_angle(0)
                print("Eingabe > ", end="", flush=True)
            
            # 2. RFID-Abfrage
            rfid_response = send_and_receive("RFID:GET")
            if rfid_response and rfid_response.startswith("RFID:") and rfid_response != "RFID:NONE":
                uid = rfid_response.split(":")[1]
                if uid in AUTHORIZED_UIDS:
                    threading.Thread(target=unlock_refill_station, daemon=True).start()
                else:
                    print(f"\n[RFID] ZUGANG VERWEIGERT. Unbekannte UID: {uid}")
                    print("Eingabe > ", end="", flush=True)

        time.sleep(0.5)

def start():
    """Startet den Hintergrund-Thread."""
    global is_running
    if not is_running:
        is_running = True
        threading.Thread(target=_auto_worker, daemon=True).start()

def stop():
    """Beendet den Hintergrund-Thread."""
    global is_running
    is_running = False

def enable():
    """Aktiviert die Sensor-Überwachung (auto on)."""
    global is_active
    is_active = True

def disable():
    """Deaktiviert die Sensor-Überwachung (auto off)."""
    global is_active
    is_active = False