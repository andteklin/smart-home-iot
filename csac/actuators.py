from machine import Pin

# Indicator LEDs
led_udp  = Pin(21, Pin.OUT)   # GP21
led_temp = Pin(19, Pin.OUT)   # GP19
led_heat = Pin(18, Pin.OUT)   # GP18
led_cool = Pin(16, Pin.OUT)   # GP16

# Relay
relay = Pin(15, Pin.OUT)      # GP15

def set_heater(on):
    relay.value(1 if on else 0)
    led_heat.value(1 if on else 0)
    led_cool.value(0 if on else 1)

def set_udp_indicator(on):
    led_udp.value(on)

def set_temp_indicator(on):
    led_temp.value(on)
