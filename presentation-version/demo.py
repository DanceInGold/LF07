import time
from cps_lib import steppermotor, servomotor, ultraschall, oled

def main():
    print("=== CPS Prototyp Präsentation ===")
    
    # Grundzustand herstellen
    servomotor.set_angle(0)
    
    # 1. OLED aktivieren und 120 Sekunden Timer starten
    print("\n[System] Starte OLED Display und 120-Sekunden-Timer...")
    oled.init()
    oled.start_timer(120)
    
    # 2. Warten, bis der Timer abgelaufen ist
    print("[System] Warte auf Ablauf des Timers (120s)...")
    while oled.countdown_seconds > 0:
        # Gibt alle 10 Sekunden ein Update im Terminal aus
        if oled.countdown_seconds % 10 == 0:
            print(f"  -> Timer läuft... noch {oled.countdown_seconds} Sekunden.")
        time.sleep(1)
        
    print("\n[Timer] Abgelaufen! Starte Hardware-Sequenz.\n")
    
    # 3. Erste Stepper-Funktion ausführen
    print("[Aktion 1] Starte Stepper: Radar Sweep...")
    steppermotor.muster_radar_sweep()
    
    # 4. Zweite Stepper-Funktion ausführen
    print("[Aktion 2] Starte Stepper: 180° Drehung, 5s Pause, und zurück...")
    steppermotor.muster_180_und_zurueck()
    
    # 5. Auf Ultraschallsensor warten (max 10 cm)
    print("\n[Aktion 3] Warte auf Sensor-Auslösung (Distanz <= 10 cm)...")
    sensor_ausgeloest = False
    
    while not sensor_ausgeloest:
        dist = ultraschall.get_distance()
        
        # Prüfen, ob eine gültige Messung <= 10cm vorliegt
        if 0 < dist <= 10.0:
            print(f"!!! Objekt erkannt bei {dist:.1f} cm !!!")
            sensor_ausgeloest = True
        else:
            # Kurze Pause verhindert, dass die serielle Verbindung überlastet wird
            time.sleep(0.5) 
            
    # 6. Servo Aktion ausführen
    print("[Aktion 4] Führe Sensor-Reaktion aus (Servo 0° -> 180°)...")
    servomotor.set_angle(180)
    time.sleep(2) # Kurz warten, damit das Publikum die Bewegung sieht
    
    # Aufräumen und beenden
    print("\n=== Präsentation beendet ===")
    oled.stop()
    servomotor.set_angle(0) # Servo zurück in Startposition

if __name__ == "__main__":
    main()