from __future__ import annotations
import serial
import time

# This program sends serial communication through a usb port.
# For example, to control a pi pico.

class USB:
    def __init__(self, port: str) -> None:
        self.port = port
        self.ser = None
    
    def __enter__(self) -> USB:
        self.ser = serial.Serial(self.port, 115200)
        return self
    
    def __exit__(self, exc_type, exc_value, tb) -> None:
        if self.ser is not None:
            self.ser.close()
        self.ser = None
    
    def write(self, message: str):
        if self.ser is None:
            raise Exception('Port is closed. Use "with" block to access this interface.')
        s = str.encode(message + '\n')
        self.ser.write(s)
        print(f'Just wrote {s}')
        if (self.ser.inWaiting() > 0):
            # read the bytes and convert from binary array to ASCII
            data_str = self.ser.read(self.ser.inWaiting()).decode('ascii') 
            # print the incoming string without putting a new-line
            # ('\n') automatically after every print()
            print(f'Recieving: {data_str}') 
            # Put the rest of your code you want here
            # Optional, but recommended: sleep 10 ms (0.01 sec) once per loop to let 
            # other threads on your PC run during this time.
        time.sleep(0.01) 

if __name__ == '__main__':
    with USB('COM3') as usb:
        while True:
            usb.write(input('Enter message: '))