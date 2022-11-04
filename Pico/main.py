from sys import stdin
from machine import I2C, Pin
from mcp4725 import MCP4725, BUS_ADDRESS
import led

class Pico:
    def __init__(self, mock=False):
        self.mock = mock
        if not mock:
            i2c = I2C(0, scl = Pin(1), sda = Pin(0),freq=400000)
            self.dac = MCP4725(i2c,BUS_ADDRESS[0])
        led.startup()
        try:
            self.main_loop()
        except KeyboardInterrupt:
            led.shutdown()

    def int_reader_stream(self):
        while True:
            word = stdin.readline().strip()
            if word:
                try:
                    i = int(word)
                    yield i
                except ValueError:
                    pass

    def main_loop(self):
        for i in self.int_reader_stream():
            if self.mock:
                led.decimal(i)
            else:
                assert 0 <= i < 2 ** 12
                self.dac.write(i)

if __name__ == '__main__':
    pico = Pico(mock=True)