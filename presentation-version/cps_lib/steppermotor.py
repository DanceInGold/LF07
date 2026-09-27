import time
from cps_lib.serial_link import send_and_receive

def pill_filter():
    """Bewegungsmuster 1: 120° Sweep (60° rechts, 60° links) für 2 Minuten, danach zurück zum Ursprung."""
    # Startposition ist 0. Wir fahren zuerst 60° nach rechts.
    send_and_receive("STP:341")
    
    endzeit = time.time() + 120  # Aktuelle Zeit + 120 Sekunden
    
    while time.time() < endzeit:
        # Von +60° nach -60° (insgesamt 120° Wegstrecke)
        send_and_receive("STP:-682")
        
        # Falls die 2 Minuten während der Linksdrehung ablaufen, brechen wir hier ab
        # und fahren von der aktuellen -60° Position zurück in die Mitte (0).
        if time.time() >= endzeit:
            send_and_receive("STP:341")
            return
            
        # Von -60° wieder nach +60° (insgesamt 120° Wegstrecke)
        send_and_receive("STP:682")

    # Wenn die Schleife normal beendet wird (steht gerade auf +60°), 
    # fahren wir die 60° zurück in die Mitte.
    send_and_receive("STP:-341")


def pill_drop():
    """Bewegungsmuster 2: Dreht 180°, wartet 5 Sekunden und fährt zurück."""
    send_and_receive("STP:2048")  # 180° vorwärts
    time.sleep(5)                 # 5 Sekunden warten