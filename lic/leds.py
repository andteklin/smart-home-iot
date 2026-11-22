# leds.py
from machine import Pin

led_udp  = Pin(28, Pin.OUT)   # GP28
led_temp = Pin(22, Pin.OUT)   # GP22
led_heat = Pin(21, Pin.OUT)   # GP21
led_cool = Pin(20, Pin.OUT)   # GP20

def set_udp(on):
    led_udp.value(1 if on else 0)

def set_temp(on):
    led_temp.value(1 if on else 0)

def set_heat(on):
    led_heat.value(1 if on else 0)
    led_cool.value(0 if on else 1)
