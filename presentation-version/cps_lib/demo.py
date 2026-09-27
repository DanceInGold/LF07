import time
from cps_lib import steppermotor, servomotor, ultraschall, oled

def run():
    print("\n=== CPS Prototyp Präsentation gestartet ===")
    
    # 1. Modus merken und für die Demo auf Timer zwingen
    war_modus = oled.current_mode
    oled.set_mode("timer")
    
    # Grundzustand
    servomotor.set_angle(0)
    
    print("\n[System] Starte OLED Timer...")
    oled.set_headline("Initialisiere Systeme...") 
    oled.start_timer(10) # 10 Sekunden für Testzwecke
    
    print("[System] Warte auf Ablauf des Timers...")
    while oled.countdown_seconds > 0:
        if oled.countdown_seconds % 10 == 0:
            print(f"  -> Timer läuft... noch {oled.countdown_seconds} Sekunden.")
        time.sleep(1)
        
    print("\n[Timer] Abgelaufen! Starte Hardware-Sequenz.\n")
    oled.set_headline("System aktiv!") 
    
    print("[Aktion 1] Starte Stepper: Radar Sweep...")
    steppermotor.muster_radar_sweep()
    
    print("[Aktion 2] Starte Stepper: 180° Drehung, 5s Pause, und zurück...")
    steppermotor.muster_180_und_zurueck()
    
    print("\n[Aktion 3] Warte auf Sensor-Auslösung (Distanz <= 10 cm)...")
    sensor_ausgeloest = False
    
    while not sensor_ausgeloest:
        dist = ultraschall.get_distance()
        if 0 < dist <= 10.0:
            print(f"!!! Objekt erkannt bei {dist:.1f} cm !!!")
            sensor_ausgeloest = True
        else:
            time.sleep(0.5) 
            
    print("[Aktion 4] Führe Sensor-Reaktion aus (Servo 0° -> 180°)...")
    servomotor.set_angle(180)
    time.sleep(2) 
    
    print("\n=== Präsentation beendet ===")
    servomotor.set_angle(0)
    
    # 2. Ursprünglichen Modus wiederherstellen (Standby oder Schwarz)
    oled.set_mode(war_modus)