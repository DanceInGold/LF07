import time
import threading
from datetime import datetime
from cps_lib.serial_link import send_and_receive

countdown_seconds = 0
oled_active = False

def start_timer(seconds):
    """Setzt den Timer auf eine bestimmte Sekundenzahl."""
    global countdown_seconds
    countdown_seconds = seconds

def _oled_worker():
    global countdown_seconds, oled_active
    
    while oled_active:
        now = datetime.now().strftime("%H:%M")
        
        # Berechne Minuten und Sekunden
        if countdown_seconds > 0:
            mins, secs = divmod(countdown_seconds, 60)
            timer_str = f"{mins:02d}:{secs:02d}"
            countdown_seconds -= 1
        else:
            timer_str = "00:00"
            
        # Sende Format z.B.: OLED:21:38|02:15
        send_and_receive(f"OLED:{now}|{timer_str}")
        
        time.sleep(1) # Eine Sekunde warten bis zum nächsten Update

def init():
    """Startet den Display-Thread. Muss einmal am Anfang aufgerufen werden."""
    global oled_active
    if not oled_active:
        oled_active = True
        t = threading.Thread(target=_oled_worker, daemon=True)
        t.start()

def stop():
    """Stoppt die Display-Aktualisierungen."""
    global oled_active
    oled_active = False