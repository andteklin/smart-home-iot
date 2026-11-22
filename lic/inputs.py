# inputs.py
from machine import Pin, ADC
import time

pot_led = ADC(26)      # GP1
pot_temp = ADC(27)    # GP22
btn_light = Pin(15, Pin.IN, Pin.PULL_UP)

last_btn = 1
last_press_time = 0
DEBOUNCE_MS = 50

light_state = False

def set_initial_light_state(state):
    global light_state
    light_state = state

# Filter state
_led_filt = None
_temp_filt = None

POT_ALPHA = 0.2

def _ema(prev, new, alpha):
    if prev is None:
        return new
    return alpha * new + (1 - alpha) * prev

def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def read_pots():
    global _led_filt, _temp_filt
    
    s_led = 0
    s_temp = 0
    N = 4

    for _ in range(N):
        s_led  += pot_led.read_u16()
        s_temp += pot_temp.read_u16()

    led_raw  = s_led  // N
    temp_raw = s_temp // N

    brightness = map_value(led_raw, 128, 65535, 0, 100)
    temp = map_value(temp_raw, 80, 65535, 59, 86)

    # Apply EMA filter
    _led_filt  = _ema(_led_filt,  brightness,  POT_ALPHA)
    _temp_filt = _ema(_temp_filt, temp, POT_ALPHA)

    # Return filtered values
    return int(round(_led_filt)), _temp_filt

def read_button():
    global last_btn, last_press_time, light_state
    btn = btn_light.value()
    now = time.ticks_ms()

    if btn == 0 and last_btn == 1:
        if time.ticks_diff(now, last_press_time) > DEBOUNCE_MS:
            light_state = not light_state
            last_press_time = now

    last_btn = btn
    return light_state