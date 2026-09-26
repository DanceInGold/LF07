from cps_lib.serial_link import send_and_receive

def get_distance():
    """Fordert die Distanz an und extrahiert den Float-Wert aus der Antwort."""
    response = send_and_receive("US:GET")
    
    # response sieht so aus: "DIST:15.5"
    if response and response.startswith("DIST:"):
        try:
            value_str = response.split(":")[1]
            return float(value_str)
        except ValueError:
            return -1.0
    return -1.0