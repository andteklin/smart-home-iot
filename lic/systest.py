from machine import Pin, ADC
import time

# -----------------------------
# PIN DEFINITIONS (from your map)
# -----------------------------

# LED BAR (10 LEDs)
led_bar = [
    Pin(11, Pin.OUT),   # LED BAR 1
    Pin(10, Pin.OUT),   # LED BAR 2
    Pin(9, Pin.OUT),   # LED BAR 3
    Pin(8, Pin.OUT),   # LED BAR 4
    Pin(7, Pin.OUT),   # LED BAR 5
    Pin(7, Pin.OUT),   # LED BAR 6
    Pin(6, Pin.OUT),   # LED BAR 7
    Pin(5, Pin.OUT),   # LED BAR 8
    Pin(4, Pin.OUT),  # LED BAR 9
    Pin(3, Pin.OUT)   # LED BAR 10
]

# Indicator LEDs
led_udp   = Pin(28, Pin.OUT)   # LED IDI UDP
led_temp  = Pin(22, Pin.OUT)   # LED IDI TEMP
led_heat  = Pin(21, Pin.OUT)   # LED IDI HEAT
led_cool  = Pin(20, Pin.OUT)   # LED IDI COOL

# Inputs
pot_led_ctrl  = ADC(26)   # GP1
pot_temp_ctrl = ADC(27)  # GP22
btn_led_ctrl  = Pin(15, Pin.IN, Pin.PULL_UP)

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def read_adc(adc):
    return adc.read_u16()  # 0–65535

def clear_leds():
    # LED bar
    for led in led_bar:
        led.value(0)

    # Indicator LEDs
    led_udp.value(0)
    led_temp.value(0)
    led_heat.value(0)
    led_cool.value(0)

    print("All LEDs cleared.")
# -----------------------------
# MAIN TEST LOOP
# -----------------------------

print("Starting hardware test...")

light_state = False
last_btn = 1
try:
    while True:
        # --- Read button (toggle light state) ---
        btn = btn_led_ctrl.value()
        if btn == 0 and last_btn == 1:
            light_state = not light_state
            print("Light toggled:", light_state)
        last_btn = btn

        # --- Read potentiometers ---
        pot_led_val = read_adc(pot_led_ctrl)
        pot_temp_val = read_adc(pot_temp_ctrl)

        # --- LED BAR test (brightness pot controls how many LEDs light) ---
        bar_level = int((pot_led_val / 65535) * 10)
        for i, led in enumerate(led_bar):
            led.value(1 if i < bar_level else 0)

        # --- Indicator LEDs ---
        led_udp.value((time.ticks_ms() // 500) % 2)   # blink every 0.5s
        led_temp.value(1 if pot_temp_val > 40000 else 0)
        led_heat.value(light_state)
        led_cool.value(not light_state)

        # --- Print debug info ---
        print("LED pot:", pot_led_val, "Temp pot:", pot_temp_val)

        time.sleep(0.1)
except KeyboardInterrupt:
    clear_leds()