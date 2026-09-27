import time
import threading
from datetime import datetime
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.core.render import canvas
from PIL import ImageFont

timer_end_time = 0
oled_active = False
current_headline = "Nächste Ausgabe in..."
current_mode = "standby" # Modi: "standby", "timer", "loading", "off"

# Ladebalken Variablen
loading_text = ""
loading_start_time = 0
loading_duration = 0
loading_progress_override = -1.0

device = None

try:
    font_default = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    font_standby_date = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    font_standby_time = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
except IOError:
    print("[OLED] Warnung: TrueType Fonts nicht gefunden. Nutze Fallback.")
    font_default = font_standby_date = font_standby_time = ImageFont.load_default()

def start_timer(seconds):
    global timer_end_time
    timer_end_time = time.time() + seconds

def get_remaining_seconds():
    """Gibt die verbleibenden Sekunden für den Timer zurück."""
    return max(0, int(timer_end_time - time.time()))

def set_headline(text):
    global current_headline
    current_headline = text

def set_mode(mode):
    global current_mode
    current_mode = mode

def start_loading(text, duration=0):
    """
    Startet den Ladebalken. 
    duration > 0: Füllt sich über die Zeit (stoppt bei 95%).
    duration == 0: Erzeugt einen kontinuierlichen Endlos-Loop.
    """
    global current_mode, loading_text, loading_start_time, loading_duration, loading_progress_override
    loading_text = text
    loading_duration = duration
    loading_start_time = time.time()
    loading_progress_override = -1.0
    current_mode = "loading"

def finish_loading_step():
    """Füllt den Balken auf 100% und wartet 0.5s für den visuellen Effekt."""
    global loading_progress_override
    loading_progress_override = 1.0
    time.sleep(0.5)

def get_text_width(draw, text, font):
    try:
        return draw.textlength(text, font=font)
    except AttributeError:
        width, _ = draw.textsize(text, font=font)
        return width

def _oled_worker():
    global oled_active, current_headline, current_mode
    
    while oled_active:
        now_time = datetime.now().strftime("%H:%M")
        now_date = datetime.now().strftime("%d.%m.%Y")
        
        with canvas(device) as draw:
            if current_mode == "off":
                pass
                
            elif current_mode == "standby":
                w_date = get_text_width(draw, now_date, font_standby_date)
                w_time = get_text_width(draw, now_time, font_standby_time)
                
                x_date = (128 - w_date) / 2
                x_time = (128 - w_time) / 2
                
                draw.text((x_date, 10), now_date, font=font_standby_date, fill="white")
                draw.text((x_time, 26), now_time, font=font_standby_time, fill="white")
                
            elif current_mode == "timer":
                remaining = get_remaining_seconds()
                mins, secs = divmod(remaining, 60)
                timer_str = f"{mins:02d}:{secs:02d}"
                    
                draw.text((95, 0), now_time, fill="white")
                draw.text((0, 20), current_headline, fill="white")
                draw.text((45, 40), timer_str, fill="white")
                
            elif current_mode == "loading":
                # Äußerer Rahmen (Rechteck)
                draw.rectangle((10, 40, 118, 55), outline="white", fill="black")
                
                if loading_progress_override >= 0:
                    progress = loading_progress_override
                else:
                    elapsed = time.time() - loading_start_time
                    if loading_duration > 0:
                        # Berechne Füllstand, kappe bei 95%, bis die Aktion wirklich fertig ist
                        progress = elapsed / loading_duration
                        if progress > 0.95:
                            progress = 0.95 
                    else:
                        # Unbekannte Dauer (Endlos-Loop, füllt sich alle 1.5s neu)
                        progress = (elapsed % 1.5) / 1.5
                
                # Innere Füllung (1 Pixel Abstand -> startet bei 12, endet max. bei 116)
                fill_width = int(104 * progress)
                if fill_width > 0:
                    draw.rectangle((12, 42, 12 + fill_width, 53), outline="white", fill="white")
                    
                # Aktions-Text zentriert über dem Ladebalken
                w_text = get_text_width(draw, loading_text, font_default)
                x_text = (128 - w_text) / 2
                draw.text((x_text, 18), loading_text, font=font_default, fill="white")
                
        # 10 FPS für extrem flüssige Balken-Animationen
        time.sleep(0.1) 

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
    time.sleep(0.2) 
    if device:
        device.clear()