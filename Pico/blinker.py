import time
import sys
from machine import Pin

# initialise the on board led
led = Pin(25, Pin.OUT)

# Initilaise the I2C


while True:
    led(1)
    cmd = sys.stdin.readline().strip()
    try:
        i = int(cmd)
    except ValueError:
        i = 3
    for _ in range(2*i):
        led.toggle()
        time.sleep(0.5)
    time.sleep(1)