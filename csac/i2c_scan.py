from machine import Pin, I2C

i2c = I2C(0, scl=Pin(13), sda=Pin(12))
print(i2c.scan())
