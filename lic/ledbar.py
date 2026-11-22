# ledbar.py
from machine import Pin

# LED bar pins from GP2 → GP12
LED_PINS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
LED_PINS = LED_PINS[::-1]
leds = [Pin(p, Pin.OUT) for p in LED_PINS]

def set_bar_level(level):
    """
    level: 0–100 brightness percentage
    Maps to 0–11 LEDs
    """
    # Convert 0–100% → 0–11 LEDs
    num_leds = int((level / 100) * len(leds))

    for i, led in enumerate(leds):
        led.value(1 if i < num_leds else 0)
