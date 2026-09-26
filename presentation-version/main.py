import time
import threading
from cps_lib import steppermotor, servomotor, ultraschall, demo # <-- demo importiert
from cps_lib.serial_link import send_and_receive

automatik_aktiv = False 
programm_laeuft = True

def automatik_task():
    global automatik_aktiv, programm_laeuft
    while programm_laeuft:
        if automatik_aktiv:
            dist = ultraschall.get_distance()
            if 0 < dist < 15.0:
                print(f"\n[Auto] Hindernis ({dist:.1f}cm)! Ausweichmuster.")
                servomotor.set_angle(0)
                steppermotor.muster_radar_sweep()
            elif 15.0 <= dist < 50.0:
                print(f"\n[Auto] Objekt in Reichweite ({dist:.1f}cm).")
                servomotor.set_angle(180)
                send_and_receive("STP:200") 
        time.sleep(0.5)

def main():
    global automatik_aktiv, programm_laeuft
    
    print("CPS Prototyp initialisiert...")
    servomotor.set_angle(90)
    
    auto_thread = threading.Thread(target=automatik_task)
    auto_thread.start()
    
    print("\n--- CPS Steuerungs-Konsole ---")
    print("Befehle:")
    print(" auto on     -> Startet die Sensor-if-cases")
    print(" auto off    -> Stoppt die Sensor-if-cases")
    print(" srv <0-180> -> Servo manuell bewegen (z.B. 'srv 45')")
    print(" stp 1       -> Stepper: Radar-Muster manuell")
    print(" stp 2       -> Stepper: 180°-Muster manuell")
    print(" demo        -> Startet die vordefinierte Präsentations-Sequenz") # <-- Neu
    print(" exit        -> Beendet das Programm")
    
    while programm_laeuft:
        try:
            cmd = input("\nEingabe > ").strip().lower()
            
            if cmd == "exit":
                programm_laeuft = False
                break
                
            elif cmd == "demo":
                # Verhindern, dass Demo und Automatik gleichzeitig laufen
                if automatik_aktiv:
                    print("Fehler: Bitte deaktiviere zuerst die Automatik mit 'auto off', bevor du die Demo startest.")
                else:
                    demo.run() # <-- Hier wird die Demo aufgerufen
                
            elif cmd == "auto on":
                automatik_aktiv = True
                print(">> Automatik AKTIVIERT")
                
            elif cmd == "auto off":
                automatik_aktiv = False
                print(">> Automatik DEAKTIVIERT")
                
            elif cmd.startswith("srv "):
                try:
                    winkel = int(cmd.split()[1])
                    servomotor.set_angle(winkel)
                    print(f">> Servo auf {winkel}°")
                except ValueError:
                    print("Fehler: Bitte einen gültigen Winkel eingeben (z.B. srv 90).")
                    
            elif cmd.startswith("stp "):
                try:
                    muster = int(cmd.split()[1])
                    if muster == 1:
                        print(">> Führe Stepper-Muster 1 aus...")
                        steppermotor.pill_filter()
                    elif muster == 2:
                        print(">> Führe Stepper-Muster 2 aus...")
                        steppermotor.pill_drop()
                    else:
                        print("Unbekanntes Muster.")
                except ValueError:
                    print("Fehler: Bitte 'stp 1' oder 'stp 2' eingeben.")
            
            elif cmd != "":
                print("Unbekannter Befehl. Bitte erneut versuchen.")
                
        except KeyboardInterrupt:
            programm_laeuft = False
            break

    print("\nFahre System herunter...")
    auto_thread.join()
    print("Beendet.")

if __name__ == "__main__":
    main()