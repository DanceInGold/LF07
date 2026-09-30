import time
from cps_lib import steppermotor, servomotor, demo, oled, normal_mode, mqtt_sync
from cps_lib.serial_link import send_and_receive


programm_laeuft = True

def main():
    global programm_laeuft
    
    print("CPS Prototyp initialisiert...")
    oled.init()
    oled.set_mode("standby") 

    servomotor.set_angle(0)
    send_and_receive("SRV2:0") # Schloss direkt beim Start sichern
    
    # Automatik-Thread im Hintergrund starten (aber noch pausiert)
    normal_mode.start()
    
    print("\n--- CPS Steuerungs-Konsole ---")
    print("Befehle:")
    print(" auto on     -> Startet Sensor-Überwachung (Ultraschall & RFID)")
    print(" auto off    -> Stoppt Sensor-Überwachung")
    print(" stdby on    -> Aktiviert das OLED Standby-Layout (Uhrzeit/Datum)")
    print(" stdby off   -> Deaktiviert das Display (Schwarz)")
    print(" srv 1/2 <X> -> Servo 1 oder 2 manuell bewegen (z.B. 'srv 2 180')")
    print(" stp 1/2/<X> -> Stepper steuern (Muster 1/2 oder Schritte)")
    print(" demo        -> Startet die vordefinierte Präsentations-Sequenz")
    print(" exit        -> Beendet das Programm")
    
    while programm_laeuft:
        try:
            cmd = input("\nEingabe > ").strip().lower()
            
            if cmd == "exit":
                programm_laeuft = False
                break
                
            elif cmd == "demo":
                if normal_mode.is_active:
                    print("Fehler: Bitte deaktiviere zuerst die Automatik mit 'auto off', bevor du die Demo startest.")
                else:
                    demo.run() 
                
            elif cmd == "stdby on":
                oled.set_mode("standby")
                print(">> OLED Standby-Modus AKTIVIERT")
                
            elif cmd == "stdby off":
                oled.set_mode("off")
                print(">> OLED Display DEAKTIVIERT (Schwarz)")
                
            elif cmd == "auto on":
                normal_mode.enable()
                print(">> Automatik AKTIVIERT")
                
            elif cmd == "auto off":
                normal_mode.disable()
                print(">> Automatik DEAKTIVIERT")
                
            elif cmd.startswith("srv "):
                try:
                    parts = cmd.split()
                    servo_id = parts[1]
                    winkel = int(parts[2])
                    
                    if servo_id == "1":
                        servomotor.set_angle(winkel)
                    elif servo_id == "2":
                        send_and_receive(f"SRV2:{winkel}")
                    else:
                        print("Fehler: Bitte wähle Servo 1 oder 2 (z.B. 'srv 2 90').")
                        continue
                    print(f">> Servo {servo_id} auf {winkel}°")
                except (IndexError, ValueError):
                    print("Fehler: Befehl muss so aussehen: 'srv <1|2> <winkel>'")
                    
            elif cmd.startswith("stp "):
                try:
                    wert = int(cmd.split()[1])
                    if wert == 1:
                        print(">> Führe Stepper-Muster 1 aus...")
                        steppermotor.pill_filter()
                    elif wert == 2:
                        print(">> Führe Stepper-Muster 2 aus...")
                        steppermotor.pill_drop()
                    else:
                        print(f">> Bewege Stepper um {wert} Schritte...")
                        send_and_receive(f"STP:{wert}")
                except ValueError:
                    print("Fehler: Bitte eine gültige Zahl eingeben.")
            
            elif cmd != "":
                print("Unbekannter Befehl. Bitte erneut versuchen.")
                
        except KeyboardInterrupt:
            programm_laeuft = False
            break

    print("\nFahre System herunter...")
    normal_mode.stop()
    oled.stop() 
    print("Beendet.")

if __name__ == "__main__":
    main()