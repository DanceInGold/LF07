import time
import threading
from datetime import datetime
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.core.render import canvas
from PIL import ImageFont

countdown_seconds = 0
oled_active = False
current_headline = "Nächste Ausgabe in..." # Jetzt dynamisch anpassbar! (Auch Umlaute gehen jetzt problemlos)

# Globale Variablen für das Display
device = None

def start_timer(seconds):
    """Setzt den Timer auf eine bestimmte Sekundenzahl."""
    global countdown_seconds
    countdown_seconds = seconds

def set_headline(text):
    """Ändert die Überschrift dynamisch zur Laufzeit."""
    global current_headline
    current_headline = text

def _oled_worker():
    global countdown_seconds, oled_active, current_headline
    
    # Optional: Wenn du TrueType Fonts (.ttf) auf dem Pi hast, kannst du sie hier laden
    # font = ImageFont.truetype("arial.ttf", 14) 
    
    while oled_active:
        now = datetime.now().strftime("%H:%M")
        
        if countdown_seconds > 0:
            mins, secs = divmod(countdown_seconds, 60)
            timer_str = f"{mins:02d}:{secs:02d}"
            countdown_seconds -= 1
        else:
            timer_str = "00:00"
            
        # Zeichnet den aktuellen Frame
        with canvas(device) as draw:
            # draw.text((x, y), Text, fill="white")
            
            # Uhrzeit oben rechts
            draw.text((95, 0), now, fill="white")
            
            # Dynamische Überschrift
            draw.text((0, 20), current_headline, fill="white")
            
            # Großer Timer (ohne externe TTF-Font laden wir den Standard-Font etwas anders, 
            # aber man kann ihn durch Pillow extrem flexibel anpassen)
            draw.text((45, 40), timer_str, fill="white")
            
        time.sleep(1)

def init():
    """Initialisiert das Display am I2C-Bus des Raspberry Pi und startet den Thread."""
    global oled_active, device
    
    if not oled_active:
        try:
            # Port 1 ist der Standard I2C Port am Raspberry Pi
            serial = i2c(port=1, address=0x3C)
            device = sh1106(serial)
            
            oled_active = True
            t = threading.Thread(target=_oled_worker, daemon=True)
            t.start()
            print("[OLED] Display erfolgreich am Raspberry Pi initialisiert.")
        except Exception as e:
            print(f"[OLED] Fehler bei der Initialisierung: {e}")

def stop():
    """Stoppt die Display-Aktualisierungen und leert das Display."""
    global oled_active, device
    oled_active = False
    time.sleep(1) # Kurz warten bis der Worker-Thread beendet ist
    if device:
        device.clear()