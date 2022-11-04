from machine import Pin
from math import log10, floor
from time import sleep

led = Pin(25, Pin.OUT)

def toggle():
    led.toggle()

def on():
    led(1)

def off():
    led(0)

def blink(n, time, offtime=None):
    if offtime is None:
        offtime = time
    off()
    for _ in range(n):
        led.toggle()
        sleep(time)
        led.toggle()
        sleep(offtime)

def decimal(n):
    """
    Send flashes representing the decimal representation of an integer.
    1-9 short flashes for a non-zero symbol, and one long flash for a zero.
    Great for troubleshooting USB serial communication.
    """
    if n == 0: # Handle special case
        blink(1, 0.8)
        return

    N = floor(log10(n)) # Position of largest integer   
    while N >= 0:       # Loop over all decimal symbols of n, from largest to smallest
        i = n // (10 ** N)  # Get largest decimal symbol
        if i == 0:
            blink(1, 0.8, 0.2)
        else:
            blink(i, 0.2)
        sleep(0.5)
        n = n - i * 10 ** N # Remove largest symbol
        N = N - 1           # Reduce position by 1
    

def startup():
    blink(3, 0.4)
    blink(3, 0.1)

def shutdown():
    blink(3, 0.1)
    blink(3, 0.4)