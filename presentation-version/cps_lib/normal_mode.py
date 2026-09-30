import time
import threading
import json
import os
from datetime import datetime
from cps_lib import demo, http_sync
from cps_lib.serial_link import send_and_receive

# Mapping der Python-Wochentage (0 = Montag) auf die deutschen JSON-Kürzel
WEEKDAYS_DE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

is_running = False
is_active = False
last_triggered_minute = ""

def load_authorized_uids():
    """Lädt die erlaubten RFIDs live aus der JSON-Datei."""
    filepath = os.path.join(os.getcwd(), "configs", "rfid_cards.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            cards = json.load(f)
            # Erstellt ein Dictionary: {"53FBEB12": "Zitrus", ...}, aber nur wenn active == true
            return {card["uid"]: card.get("person", "Unbekannt") for card in cards if card.get("active", False)}
    except FileNotFoundError:
        print(f"\n[Warnung] Konnte '{filepath}' nicht finden.")
        return {}
    except json.JSONDecodeError:
        print(f"\n[Fehler] Die Datei {filepath} enthält ungültiges JSON.")
        return {}
    except Exception as e:
        print(f"\n[Fehler] Unerwarteter Fehler beim Lesen der RFID Config: {e}")
        return {}

def unlock_refill_station(person_name):
    """Öffnet das Schloss asynchron für 5 Sekunden."""
    print(f"\n[RFID] Autorisierung erfolgreich! Hallo {person_name}. Öffne Nachfüll-Schloss...")
    send_and_receive("SRV2:180")
    time.sleep(5)
    send_and_receive("SRV2:0")
    print("\n[RFID] Nachfüll-Schloss wieder verriegelt.")
    print("Eingabe > ", end="", flush=True)

def load_schedule():
    """Lädt den Medikamentenplan live aus der JSON-Datei."""
    filepath = os.path.join(os.getcwd(), "configs", "medication_plans.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"\n[Warnung] Konnte '{filepath}' nicht finden.")
        return []
    except json.JSONDecodeError:
        print(f"\n[Fehler] Die Datei {filepath} enthält ungültiges JSON.")
        return []
    except Exception as e:
        print(f"\n[Fehler] Unerwarteter Fehler beim Lesen der Med-Config: {e}")
        return []

def _auto_worker():
    global is_active, is_running, last_triggered_minute
    
    while is_running:
        if is_active:
            # --- 1. SCHEDULER (Medikamenten-Plan prüfen) ---
            now = datetime.now()
            current_time_str = now.strftime("%H:%M")
            current_weekday = WEEKDAYS_DE[now.weekday()]
            
            if current_time_str != last_triggered_minute:
                plaene = load_schedule()
                
                for plan in plaene:
                    if not plan.get("active", False):
                        continue
                    
                    if plan.get("time") == current_time_str and current_weekday in plan.get("weekdays", []):
                        print(f"\n[Scheduler] Medikament fällig: {plan.get('amount')}x {plan.get('medication')} für {plan.get('patient')}!")
                        last_triggered_minute = current_time_str
                        
                        demo.run()
                        
                        print("\n[Scheduler] Ausgabe-Zyklus beendet. Kehre in Überwachungs-Modus zurück.")
                        print("Eingabe > ", end="", flush=True)
                        break 

            # --- 2. RFID-ABFRAGE (Nachfüll-Schloss) ---
            rfid_response = send_and_receive("RFID:GET")
            if rfid_response and rfid_response.startswith("RFID:") and rfid_response != "RFID:NONE":
                uid = rfid_response.split(":")[1]
                
                # JSON-Datei nur exakt in dem Moment laden, wenn ein Chip vorgehalten wird!
                authorized_cards = load_authorized_uids()
                
                if uid in authorized_cards:
                    person_name = authorized_cards[uid]
                    threading.Thread(target=unlock_refill_station, args=(person_name,), daemon=True).start()
                else:
                    print(f"\n[RFID] ZUGANG VERWEIGERT. Unbekannte oder inaktive UID: {uid}")
                    print("Eingabe > ", end="", flush=True)

        time.sleep(0.5)

def start():
    global is_running
    if not is_running:
        # 1. Initiale HTTP-Synchronisation ausführen
        http_sync.sync_all()
        
        # 2. Hintergrund-Worker starten
        is_running = True
        threading.Thread(target=_auto_worker, daemon=True).start()

def stop():
    global is_running
    is_running = False

def enable():
    global is_active
    is_active = True

def disable():
    global is_active
    is_active = False