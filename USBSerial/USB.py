import serial
import time

# This program sends serial communication through a usb port.
# For example, to control a pi pico.

class USB:
    def __init__(self, port):
        self.port = port
        self.ser = None
    
    def __enter__(self):
        self.ser = serial.Serial(self.port, 115200)
        print(f'Opened connection to port {self.port}')
        return self
    
    def __exit__(self, exc_type, exc_value, tb):
        if self.ser is not None:
            print('Closing...')
            self.ser.close()
            print('Closed')
        self.ser = None
    
    def write(self, message: str):
        if self.ser is None:
            raise Exception('Port is closed. Use "with" block to access this interface.')
        s = str.encode(message + '\n')
        print(f'Writing message {s}')
        self.ser.write(s)
        print('Written')
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