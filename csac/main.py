# main.py (Pico 2)
import time
from udp import init_udp, send_msg, recv_msg
from sensor import read_filtered_temp_f as read_filtered_temp
from actuators import set_heater, set_udp_indicator, set_temp_indicator
from wifi import connect_wifi

# --- CONFIG ---
UI_IP = "192.168.4.106"   # IP of Pico 1
wlan = connect_wifi()
sock = init_udp()

# --- Control parameters ---
HEAT_ON_DELTA  = 0.5     # turn ON when 0.5°F below setpoint
HEAT_OFF_DELTA = 0.2     # turn OFF when within 0.2°F of setpoint

PREDICT_HORIZON = 2.0    # seconds to look ahead (small for slow thermal system)

MIN_ON_TIME  = 3         # seconds
MIN_OFF_TIME = 3

# --- State ---
setpoint = 70.0
heater_on = False
last_rx = time.ticks_ms()

last_temp = None
last_time = None

last_on_time = 0
last_off_time = 0


while True:
    now = time.ticks_ms()

    # --- Receive commands from UI Pico ---
    msg, ip = recv_msg(sock)
    if msg:
        last_rx = now
        set_udp_indicator(True)

        if msg.startswith("SET:"):
            setpoint = float(msg.split(":")[1])

    # UDP timeout indicator
    if time.ticks_diff(now, last_rx) > 1000:
        set_udp_indicator(False)

    # --- Read filtered temperature ---
    temp = read_filtered_temp()
    set_temp_indicator(True)

    # --- Compute derivative (rate of change) ---
    predicted_temp = temp
    if last_temp is not None:
        dt = time.ticks_diff(now, last_time) / 1000.0
        if dt > 0:
            dT = temp - last_temp
            rate = dT / dt
            predicted_temp = temp + rate * PREDICT_HORIZON

    # --- HEATER CONTROL LOGIC ---

    # 1. Predictive cutoff only when close to setpoint
    if heater_on and temp >= setpoint - 0.5:
        if predicted_temp >= setpoint:
            if time.ticks_diff(now, last_on_time) > MIN_ON_TIME * 1000:
                heater_on = False
                last_off_time = now

    # 2. Hysteresis ON logic
    if not heater_on and temp <= setpoint - HEAT_ON_DELTA:
        if time.ticks_diff(now, last_off_time) > MIN_OFF_TIME * 1000:
            heater_on = True
            last_on_time = now

    # 3. Hysteresis OFF logic (backup)
    if heater_on and temp >= setpoint - HEAT_OFF_DELTA:
        if time.ticks_diff(now, last_on_time) > MIN_ON_TIME * 1000:
            heater_on = False
            last_off_time = now

    # --- Apply heater state ---
    set_heater(heater_on)

    # --- Save for next iteration ---
    last_temp = temp
    last_time = now

    # --- Send temperature + heater state back to Pico 1 ---
    send_msg(sock, UI_IP, "TEMP:%.2f" % temp)
    send_msg(sock, UI_IP, "HEAT:%d" % (1 if heater_on else 0))

    time.sleep(0.2)
