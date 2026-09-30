import os
import json
import threading
import paho.mqtt.client as mqtt

# MQTT Konfiguration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPIC_MEDS = "cps/config/medication"
TOPIC_RFID = "cps/config/rfid"

mqtt_client = None
is_running = False

def on_connect(client, userdata, flags, rc):
    """Wird aufgerufen, sobald die Verbindung zum Broker steht."""
    if rc == 0:
        print(f"\n[MQTT] Verbunden mit Broker ({MQTT_BROKER}). Lausche auf Config-Updates...")
        client.subscribe(TOPIC_MEDS)
        client.subscribe(TOPIC_RFID)
    else:
        print(f"\n[MQTT] Fehler bei der Verbindung. Return code: {rc}")

def on_message(client, userdata, msg):
    """Wird aufgerufen, wenn eine neue Nachricht auf einem abonnierten Topic reinkommt."""
    try:
        # Nachricht dekodieren und als JSON parsen (validiert, ob es echtes JSON ist)
        payload_str = msg.payload.decode("utf-8")
        json_data = json.loads(payload_str)
        
        # Ziel-Datei bestimmen
        if msg.topic == TOPIC_MEDS:
            filename = "medication_plans.json"
        elif msg.topic == TOPIC_RFID:
            filename = "rfid_cards.json"
        else:
            return

        # Speichern im configs Ordner
        filepath = os.path.join(os.getcwd(), "configs", filename)
        
        # Ordner erstellen, falls er nicht existiert
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
            
        print(f"\n[MQTT] Update empfangen! Erfolgreich gespeichert: {filename}")
        print("Eingabe > ", end="", flush=True)
        
    except json.JSONDecodeError:
        print(f"\n[MQTT] Fehler: Empfangene Daten auf {msg.topic} sind kein gültiges JSON.")
        print("Eingabe > ", end="", flush=True)
    except Exception as e:
        print(f"\n[MQTT] Unerwarteter Fehler beim Speichern: {e}")
        print("Eingabe > ", end="", flush=True)

def start():
    """Startet den MQTT Client in einem eigenen Hintergrund-Thread."""
    global mqtt_client, is_running
    if not is_running:
        try:
            # Paho-MQTT Client initialisieren
            mqtt_client = mqtt.Client()
            mqtt_client.on_connect = on_connect
            mqtt_client.on_message = on_message
            
            # Verbinden
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            
            # Startet die Netzwerk-Schleife im Hintergrund (Daemon-Thread)
            mqtt_client.loop_start()
            is_running = True
        except Exception as e:
            print(f"[MQTT] Konnte nicht gestartet werden: {e}")

def stop():
    """Beendet den MQTT Client sauber."""
    global mqtt_client, is_running
    if is_running and mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        is_running = False