import time
import threading
from datetime import datetime
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.core.render import canvas
from PIL import ImageFont

countdown_seconds = 0
oled_active = False
current_headline = "Nächste Ausgabe in..."
is_standby = False # Steuert den Anzeige-Modus

device = None

# Echte Schriftarten (TrueType) vom Raspberry Pi OS laden
try:
    # Font für normales Layout
    font_default = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    
    # Fonts für Standby (Datum klein, Uhrzeit massiv)
    font_standby_date = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    font_standby_time = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
except IOError:
    print("[OLED] Warnung: TrueType Fonts nicht gefunden. Nutze Fallback.")
    font_default = font_standby_date = font_standby_time = ImageFont.load_default()

def start_timer(seconds):
    global countdown_seconds
    countdown_seconds = seconds

def set_headline(text):
    global current_headline
    current_headline = text

def set_standby(state):
    """Aktiviert oder deaktiviert den Standby-Bildschirm."""
    global is_standby
    is_standby = state

def get_text_width(draw, text, font):
    """Hilfsfunktion für Kompatibilität zwischen alten und neuen Pillow Versionen."""
    try:
        return draw.textlength(text, font=font)
    except AttributeError:
        width, _ = draw.textsize(text, font=font)
        return width

def _oled_worker():
    global countdown_seconds, oled_active, current_headline, is_standby
    
    while oled_active:
        now_time = datetime.now().strftime("%H:%M")
        now_date = datetime.now().strftime("%d.%m.%Y")
        
        with canvas(device) as draw:
            if is_standby:
                # --- STANDBY LAYOUT ---
                # 1. Exakte Pixelbreiten berechnen
                w_date = get_text_width(draw, now_date, font_standby_date)
                w_time = get_text_width(draw, now_time, font_standby_time)
                
                # 2. X-Position berechnen (Bildschirm ist 128px breit -> Zentrieren)
                x_date = (128 - w_date) / 2
                x_time = (128 - w_time) / 2
                
                # 3. Zeichnen (Y-Positionen manuell für perfekten Abstand gewählt)
                draw.text((x_date, 10), now_date, font=font_standby_date, fill="white")
                draw.text((x_time, 26), now_time, font=font_standby_time, fill="white")
                
            else:
                # --- NORMALES TIMER LAYOUT ---
                if countdown_seconds > 0:
                    mins, secs = divmod(countdown_seconds, 60)
                    timer_str = f"{mins:02d}:{secs:02d}"
                    countdown_seconds -= 1
                else:
                    timer_str = "00:00"
                    
                draw.text((95, 0), now_time, font=font_default, fill="white")
                draw.text((0, 20), current_headline, font=font_default, fill="white")
                
                # Auch den großen Timer zentrieren wir optisch in der Mitte
                w_timer = get_text_width(draw, timer_str, font_standby_time)
                x_timer = (128 - w_timer) / 2
                draw.text((x_timer, 35), timer_str, font=font_standby_time, fill="white")
                
        time.sleep(1)

def init():
    global oled_active, device
    if not oled_active:
        try:
            serial = i2c(port=1, address=0x3C)
            device = sh1106(serial)
            oled_active = True
            threading.Thread(target=_oled_worker, daemon=True).start()
        except Exception as e:
            print(f"[OLED] Fehler: {e}")

def stop():
    global oled_active, device
    oled_active = False
    time.sleep(1) 
    if device:
        device.clear()