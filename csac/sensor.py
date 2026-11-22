from machine import Pin, I2C
from bme280 import BME280

# Your pinout:
# SCL = GP12
# SDA = GP13

i2c = I2C(0, scl=Pin(13), sda=Pin(12))
bme = BME280(i2c=i2c)

alpha = 0.9
filtered_temp = None

def read_filtered_temp_c():
    global filtered_temp
    t_raw = bme.read_compensated_data()[0] / 100  # convert to °C

    if filtered_temp is None:
        filtered_temp = t_raw
    else:
        filtered_temp = alpha * t_raw + (1 - alpha) * filtered_temp

    return filtered_temp

def read_filtered_temp_f():
    global filtered_temp
    t_raw_c = bme.read_compensated_data()[0] / 100  # °C

    if filtered_temp is None:
        filtered_temp = t_raw_c
    else:
        filtered_temp = alpha * t_raw_c + (1 - alpha) * filtered_temp

    # Convert to Fahrenheit
    t_f = filtered_temp * 9/5 + 32
    return t_f
