import time
import sys
from machine import I2C, Pin
import machine
from mcp4725 import MCP4725, BUS_ADDRESS

# initialise the on board led
led = Pin(25, Pin.OUT)

# Initilaise the I2C
i2c = I2C(0,scl = machine.Pin(1), sda = machine.Pin(0),freq=400000)

# Initialise the dac
dac = MCP4725(i2c,BUS_ADDRESS[0])

while True:
    # use dac.write(i) to set a the output. The DAC is 12 bit so you should choose an integer between 0 and 4096 (the maximum is 4095).
    # If well calibrated that should give you an output voltage of 10V/i
    led(0)
    cmd = sys.stdin.readline().strip()
    if True:
        for _ in range(10):
            led.toggle()
            time.sleep(0.5)
    led(1)
    time.sleep(1)
    # perform the requested action
    if True:
        for _ in range(10):
            led.toggle()
            time.sleep(0.5)
    #elif cmd == "off":
    #    led(0)
    #elif cmd == "exit":
    #    break
    #dac.write(2047)
    #led.toggle()
    #time.sleep(2)
    #dac.write(4095)
    #led.toggle()
    #time.sleep(2)