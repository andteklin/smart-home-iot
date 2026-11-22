# main.py
import time
from wifi import connect_wifi
from udp import init_udp, send_msg, recv_msg
from inputs import read_pots, read_button, set_initial_light_state
from lcd1602 import LCD
from leds import set_udp, set_temp, set_heat
from ledbar import set_bar_level
from machine import I2C, Pin
from lib.tplink_lightbulb import TPLinkLightbulb

# --- CONFIG ---
PLANT_IP = "192.168.4.196"
BULB_IP  = "192.168.4.72"

# --- WiFi ---
wlan = connect_wifi()

# --- UDP ---
sock = init_udp()

# --- LCD ---
i2c = I2C(0, scl=Pin(17), sda=Pin(16))
lcd = LCD(i2c)

# --- TP-Link bulb ---
bulb = TPLinkLightbulb(BULB_IP)

# --- State variables ---
current_temp = 0.0
heater_on = False
light_state = False
brightness = 0
setpoint = 0

last_udp_time = time.ticks_ms()

# LCD throttling (safe rate)
LCD_UPDATE_MS = 250
last_lcd_update = 0

# Last displayed LCD lines
last_lcd_line1 = ""
last_lcd_line2 = ""

# Event-driven bulb control
last_sent_on = None
last_sent_brightness = None

# Event-driven temperature control
last_sent_setpoint = None


# --- Helpers ---
def bulb_read_state():
    data = bulb.sysinfo()
    if data is None:
        return None, None
    try:
        ls = data["system"]["get_sysinfo"]["light_state"]
        return (ls.get("on_off", 0) == 1), ls.get("brightness", 0)
    except:
        return None, None


def pad16(s):
    """Pad or trim a string to exactly 16 characters (no ljust)."""
    if len(s) < 16:
        return s + (" " * (16 - len(s)))
    return s[:16]


# --- Sync bulb state at startup ---
initial_on, initial_brightness = bulb_read_state()

if initial_on is not None:
    light_state = initial_on
    set_initial_light_state(light_state)

if initial_brightness is not None:
    brightness = initial_brightness

set_bar_level(brightness if light_state else 0)


# --- Main loop ---
while True:
    now = time.ticks_ms()

    # --- Inputs ---
    brightness, setpoint = read_pots()
    button_state = read_button()

    if button_state != light_state:
        light_state = button_state

    set_bar_level(brightness if light_state else 0)

    # Event-driven temperature send
    if last_sent_setpoint is None or abs(setpoint - last_sent_setpoint) > 0.1:
        send_msg(sock, PLANT_IP, f"SET:{setpoint:.2f}")
        last_sent_setpoint = setpoint

    # Receive from Pico 2
    udp_received = False
    while True:
        msg, ip = recv_msg(sock)
        if not msg:
            break

        udp_received = True
        last_udp_time = now

        if msg.startswith("TEMP:"):
            current_temp = float(msg.split(":")[1])
            set_temp(True)

        if msg.startswith("HEAT:"):
            heater_on = (msg.split(":")[1] == "1")
            set_heat(heater_on)

    set_udp(udp_received or time.ticks_diff(now, last_udp_time) < 1000)

    # --- SAFE LCD UPDATE ---
    if time.ticks_diff(now, last_lcd_update) > LCD_UPDATE_MS:
        last_lcd_update = now

        # Build display strings
        line1 = f"T:{current_temp:4.1f}F S:{setpoint:4.1f}F"
        line2 = f"L:{'ON ' if light_state else 'OFF'} B:{brightness:3d}"

        # Pad to 16 chars
        line1 = pad16(line1)
        line2 = pad16(line2)

        # Only update changed lines
        if line1 != last_lcd_line1:
            lcd.write(0, 0, line1)
            last_lcd_line1 = line1

        if line2 != last_lcd_line2:
            lcd.write(0, 1, line2)
            last_lcd_line2 = line2

    # --- EVENT-DRIVEN BULB CONTROL ---
    if light_state != last_sent_on:
        bulb.switch(light_state)
        last_sent_on = light_state

    if light_state and brightness != last_sent_brightness:
        bulb.brightness(brightness)
        last_sent_brightness = brightness

    time.sleep(0.02)
