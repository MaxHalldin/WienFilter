from __future__ import annotations
from serial.tools import list_ports
from serial import Serial
import time
from dataclasses import dataclass

@dataclass
class USBDevice:
    vendor_id: int
    product_id: int = None
    vendor_name: str = None
    product_name: str = None

    def __str__(self):
        s = ''
        if self.vendor_name is None:
            s = s + f'Vendor ID: 0x{self.vendor_id:04x}'
        else:
            s = s + f'{self.vendor_name}'
        if self.product_name is not None:
            s = s + f' - {self.product_name}'
        elif self.product_id is not None:
            s = s + f'. Product ID 0x{self.product_id:04x}'
        return s

    def matches(self, other):
        """
        Check if USB device other could be of this type. Check vendor ID and, if available on THIS object,
        the product ID. Note that other must have product ID available if set on self.
        """   
        if self.vendor_id != self.vendor_id:
            return False
        if self.product_id is None:
            return True
        return self.product_id == other.product_id

# List of known device types
DEVICES = {
    'pico': USBDevice(0x2e8a, 0x0005, 'Raspberry PI', 'Pico')
}

class PortSelector:
    @staticmethod
    def _get_names_from_list(device: USBDevice, devicelist: list[USBDevice]) -> bool:
        matches = [target for target in devicelist if target.matches(device)]
        if matches:
            device.vendor_name = matches[0].vendor_name
            device.product_name = matches[0].product_name
            return True
        return False

    @staticmethod
    def get_devices(products: list[USBDevice] = None):
        """
        Get list of available COM ports for communication.
        If called without products, it will return all available ports.
        If called with products, it will return all ports matching description.

        Vendor and/or product name will be inserted if available 
        """
        comlist = list_ports.comports()
        return_list = []
        for port in comlist:
            device = USBDevice(port.vid, port.pid)
            if products is not None:
                if not PortSelector._get_names_from_list(device, products):
                    continue
            else:
                PortSelector._get_names_from_list(device, DEVICES.values())
            return_list.append((port.device, device))
        return return_list

class USBConnection:
    def __init__(self, port: str) -> None:
        self.port = port
        self.ser = None
    
    def __enter__(self) -> USB:
        self.ser = Serial(self.port, 115200)
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

def main():
    # Get port
    pico = DEVICES['pico']
    matches = PortSelector.get_devices([pico])
    if not matches:
        print('No pico detected :(')
        return
    port, _ = matches[0]

    # Write
    with USBConnection(port) as usb:
        while True:
            usb.write(input('Enter message: '))

if __name__ == '__main__':
    main()