# wifi.py
import network, time

SSID = "CornellCup-Web"
PASSWORD = "disneyworld!"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    wlan.connect(SSID, PASSWORD)

    print("Connecting to WiFi...")
    while not wlan.isconnected():
        time.sleep(0.2)

    print("Connected:", wlan.ifconfig())
    return wlan
