import serial
import time

# this example program controls a pi pico using serial communication trhough the usb port
# the onboard led can be turned on or off and the adc can be read out on command.
# open a serial connection

class DACInterface:
    def __init__(self, port, *, max_listed_voltage = 10, bits=12, max_safe_voltage=None):
        self.port = port
        self.ser = None
        self.listed_v = max_listed_voltage
        self.bits = bits
        self.safe_v = max_safe_voltage
    
    def __enter__(self):
        self.ser = serial.Serial(self.port, 115200)
        return self
    
    def __exit__(self, exc_type, exc_value, tb):
        if self.ser is not None:
            self.ser.close()
        self.ser = None
    
    def set_voltage(self, voltage: float):
        if self.ser is None:
            raise Exception('Port is closed. Use "with" block to access this interface.')
        if voltage > self.listed_v:
            raise ValueError(f'A voltage of {voltage} exceeds the listed DAC capability.')
        if self.safe_v is not None and voltage > self.safe_v:
            raise ValueError(f'A voltage of {voltage} exceeds the listed safe range.')
        discretization = round(voltage / self.listed_v * 2**self.bits)
        s = str.encode(str(discretization))
        print(s)
        if (self.ser.inWaiting() > 0):
            # read the bytes and convert from binary array to ASCII
            data_str = self.ser.read(self.ser.inWaiting()).decode('ascii') 
            # print the incoming string without putting a new-line
            # ('\n') automatically after every print()
            print(data_str, end='') 
            # Put the rest of your code you want here
            # Optional, but recommended: sleep 10 ms (0.01 sec) once per loop to let 
            # other threads on your PC run during this time.
            time.sleep(0.01) 

with DACInterface("COM3") as DAC:
    while True:
        try:
            x = float(input('Enter a voltage (max 10): '))
        except ValueError:
            print('Non-numerical input found. Exiting...')
            break
        try:
            DAC.set_voltage(x)
        except ValueError as e:
            print(e)