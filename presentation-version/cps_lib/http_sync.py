import urllib.request
import urllib.error
import json
import os

# --- KONFIGURATION ---
# Trage hier die IP-Adresse deines Web-Pis ein (wo der Webserver läuft)
# Beispiel: "http://192.168.178.50/pfad/zum/ordner"
WEB_PI_URL = "http://192.168.2.5:8000/mhtf/data" 

def fetch_file(filename):
    """Fordert eine spezifische JSON-Datei vom Webserver an."""
    url = f"{WEB_PI_URL}/{filename}"
    target_path = os.path.join(os.getcwd(), "configs", filename)
    
    print(f"[HTTP-Sync] Fordere '{filename}' an...")
    
    try:
        # Request mit 5 Sekunden Timeout (blockiert das System nicht endlos)
        response = urllib.request.urlopen(url, timeout=5)
        daten = response.read().decode('utf-8')
        
        # Sicherheits-Check: Ist das wirklich sauberes JSON?
        json_daten = json.loads(daten)
        
        # Ziel-Ordner erstellen, falls er noch nicht existiert
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # Datei speichern
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(json_daten, f, indent=4, ensure_ascii=False)
            
        print(f"[HTTP-Sync] Erfolgreich! '{filename}' wurde aktualisiert.")
        return True
        
    except urllib.error.URLError as e:
        print(f"[HTTP-Sync] Netzwerk-Fehler bei '{filename}': Server nicht erreichbar ({e.reason})")
    except json.JSONDecodeError:
        print(f"[HTTP-Sync] Fehler: Die heruntergeladene Datei '{filename}' ist kein gültiges JSON.")
    except Exception as e:
        print(f"[HTTP-Sync] Unerwarteter Fehler bei '{filename}': {e}")
        
    return False

def sync_all():
    """Wird einmalig beim Systemstart aufgerufen, um alle Pläne zu ziehen."""
    print("\n--- Starte initiale Datei-Synchronisation (HTTP) ---")
    fetch_file("medication_plans.json")
    fetch_file("rfid_cards.json")
    print("----------------------------------------------------\n")