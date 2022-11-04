import serial
import time

# this example program controls a pi pico using serial communication trhough the usb port
# the onboard led can be turned on or off and the adc can be read out on command.

# open a serial connection
ser = serial.Serial("COM3", 115200)

while True:
    answer = input("Turn on/off led, or adc read?")
    ser.write(str.encode(answer))
    # Check if incoming bytes are waiting to be read from the serial input 
    # buffer.
    # NB: for PySerial v3.0 or later, use property `in_waiting` instead of
    # function `inWaiting()` below!
    if (ser.inWaiting() > 0):
        # read the bytes and convert from binary array to ASCII
        data_str = ser.read(ser.inWaiting()).decode('ascii') 
        # print the incoming string without putting a new-line
        # ('\n') automatically after every print()
        print(data_str, end='') 

        # Put the rest of your code you want here
    
        # Optional, but recommended: sleep 10 ms (0.01 sec) once per loop to let 
        # other threads on your PC run during this time. 
    time.sleep(0.01) 
