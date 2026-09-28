import time
from cps_lib import steppermotor, servomotor, ultraschall, oled

def run():
    print("\n=== CPS Prototyp Präsentation gestartet ===")
    
    war_modus = oled.current_mode
    oled.set_mode("timer")
    
    servomotor.set_angle(0)
    
    print("\n[System] Starte OLED Timer...")
    oled.set_headline("Initialisiere Systeme...") 
    oled.start_timer(10) # 10 Sekunden für Testzwecke
    
    print("[System] Warte auf Ablauf des Timers...")
    while oled.get_remaining_seconds() > 0:
        # Gebe nur dann einen Print aus, wenn es eine volle 10er Sekunde ist
        if oled.get_remaining_seconds() % 10 == 0:
            print(f"  -> Timer läuft... noch {oled.get_remaining_seconds()} Sekunden.")
        time.sleep(1)
        
    print("\n[Timer] Abgelaufen! Starte Hardware-Sequenz.\n")
    
    # --- PIPELINE STAGE 1 ---
    print("[Aktion 1] Starte Stepper: Radar Sweep...")
    oled.start_loading("Medikamente werden gefiltert...", 120)
    steppermotor.pill_filter()
    oled.finish_loading_step() # Springt auf 100%
    
    # --- PIPELINE STAGE 2 ---
    print("[Aktion 2] Starte Stepper: 180° Drehung, 5s Pause, und zurück...")
    oled.start_loading("Medikamente werden vorbereitet...", 8) 
    steppermotor.pill_drop()
    oled.finish_loading_step() # Springt auf 100%
    
    # --- PIPELINE STAGE 3 ---
    print("\n[Aktion 3] Warte auf Sensor-Auslösung (Distanz <= 10 cm)...")
    oled.start_loading("Warte auf Sensor...", 0) # 0 = Endlos-Loop
    sensor_ausgeloest = False
    
    while not sensor_ausgeloest:
        dist = ultraschall.get_distance()
        if 0 < dist <= 3.0:
            print(f"!!! Objekt erkannt bei {dist:.1f} cm !!!")
            sensor_ausgeloest = True
        else:
            time.sleep(0.5) 
            
    oled.finish_loading_step() # Füllt sich schlagartig auf 100% als Bestätigung
    
    # --- PIPELINE STAGE 4 ---
    print("[Aktion 4] Führe Sensor-Reaktion aus (Servo 0° -> 180°)...")
    oled.start_loading("Wird Ausgegeben...", 5)
    servomotor.set_angle(180)
    time.sleep(2) 
    oled.finish_loading_step()
    
    print("\n=== Präsentation beendet ===")
    servomotor.set_angle(0)
    
    # Zustand zurücksetzen
    oled.set_mode(war_modus)