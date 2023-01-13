from sys import stdin
from machine import I2C, Pin
from mcp4725 import MCP4725, BUS_ADDRESS

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)  # Initialize I2C bus for communication with the DAC
dac = MCP4725(i2c, BUS_ADDRESS[0])                 # Initialize the mcp4725 package
while True:
    word = stdin.readline().strip()  # Await new line from PC
    if word:  # If line not empty
        try:
            # Try to cast recieved line to integer value, and try to set
            # recieved value on the DAC. Valid range is 0-4095 (12 bits)
            dac.write(int(word))
        except ValueError:
            # On fail, do nothing
            pass
