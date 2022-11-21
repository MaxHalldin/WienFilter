from sys import stdin
from machine import I2C, Pin
from mcp4725 import MCP4725, BUS_ADDRESS

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
dac = MCP4725(i2c, BUS_ADDRESS[0])
while True:
    word = stdin.readline().strip()
    if word:
        try:
            dac.write(int(word))
        except ValueError:
            pass
