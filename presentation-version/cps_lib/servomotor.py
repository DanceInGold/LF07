from cps_lib.serial_link import send_and_receive

def set_angle(angle):
    """Setzt den Servo auf einen Winkel zwischen 0 und 180 Grad."""
    if 0 <= angle <= 180:
        send_and_receive(f"SRV:{angle}")
    else:
        print("Fehler: Servo-Winkel muss zwischen 0 und 180 liegen.")