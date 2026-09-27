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
current_mode = "standby" # Modi: "standby", "timer", "off"

device = None

# Echte Schriftarten (TrueType) nur für den Standby-Modus laden
try:
    font_standby_date = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    font_standby_time = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
except IOError:
    print("[OLED] Warnung: TrueType Fonts nicht gefunden. Nutze Fallback.")
    font_standby_date = font_standby_time = ImageFont.load_default()

def start_timer(seconds):
    global countdown_seconds
    countdown_seconds = seconds

def set_headline(text):
    global current_headline
    current_headline = text

def set_mode(mode):
    """Setzt den Anzeige-Modus: 'standby', 'timer' oder 'off'"""
    global current_mode
    current_mode = mode

def get_text_width(draw, text, font):
    try:
        return draw.textlength(text, font=font)
    except AttributeError:
        width, _ = draw.textsize(text, font=font)
        return width

def _oled_worker():
    global countdown_seconds, oled_active, current_headline, current_mode
    
    while oled_active:
        now_time = datetime.now().strftime("%H:%M")
        now_date = datetime.now().strftime("%d.%m.%Y")
        
        with canvas(device) as draw:
            if current_mode == "off":
                # Zeichnet absolut nichts -> Display bleibt tiefschwarz
                pass
                
            elif current_mode == "standby":
                # --- STANDBY LAYOUT (Fett, zentriert) ---
                w_date = get_text_width(draw, now_date, font_standby_date)
                w_time = get_text_width(draw, now_time, font_standby_time)
                
                x_date = (128 - w_date) / 2
                x_time = (128 - w_time) / 2
                
                draw.text((x_date, 10), now_date, font=font_standby_date, fill="white")
                draw.text((x_time, 26), now_time, font=font_standby_time, fill="white")
                
            elif current_mode == "timer":
                # --- NORMALES TIMER LAYOUT (Demo-Modus) ---
                if countdown_seconds > 0:
                    mins, secs = divmod(countdown_seconds, 60)
                    timer_str = f"{mins:02d}:{secs:02d}"
                    countdown_seconds -= 1
                else:
                    timer_str = "00:00"
                    
                # Nutzt absichtlich keinen Custom-Font, um das alte, exakt passende Layout wiederherzustellen
                draw.text((95, 0), now_time, fill="white")
                draw.text((0, 20), current_headline, fill="white")
                draw.text((45, 40), timer_str, fill="white")
                
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