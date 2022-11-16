from __future__ import annotations
from typing import Iterable, Any
from serial.tools import list_ports  # type: ignore
from serial import Serial  # type: ignore
import time
from dataclasses import dataclass


@dataclass
class USBDevice:
    vendor_id: int
    product_id: int | None = None
    vendor_name: str | None = None
    product_name: str | None = None

    def __str__(self) -> str:
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

    def matches(self, other: USBDevice) -> bool:
        """
        Check if USB device other could be same device type as this. Check vendor ID and, if available on THIS object,
        the product ID. Note that other MUST have product ID available if this object has it.
        """
        if self.vendor_id != self.vendor_id:
            return False
        if self.product_id is None:
            return True
        return (self.product_id == other.product_id)


# List of known device types
# OBS OBS these are not the device names you'll find from a vendor id lookup, but just some names
# I use for verification within the project. For example, I believe the RS3005P vendor id actually refers
# to the manifacturer of the connection port, rather than the power supply.
DEVICES = {
    'pico': USBDevice(0x2e8a, 0x0005, 'Raspberry PI', 'Pico'),
    'rs': USBDevice(0x0416, 0x5011, 'RS', '3005P')
}


class PortSelector:
    @staticmethod
    def _get_names_from_list(device: USBDevice, devicelist: Iterable[USBDevice]) -> bool:
        matches = [target for target in devicelist if target.matches(device)]
        if matches:
            device.vendor_name = matches[0].vendor_name
            device.product_name = matches[0].product_name
            return True
        return False

    @staticmethod
    def get_devices(products: list[USBDevice] | None = None) -> list[tuple[str, USBDevice]]:
        """
        Get list of available COM ports for communication.
        If called without products, it will return all available ports/devices.
        If called with products, it will return all ports/devices matching the given devices.

        Vendor and/or product name will be inserted if available.

        Returns a list of (port, USBDevice) tuples
        """
        comlist = list_ports.comports()
        return_list = []
        for port in comlist:
            assert isinstance(port.vid, int)
            device = USBDevice(port.vid, port.pid)
            if products is not None:
                if not PortSelector._get_names_from_list(device, products):
                    continue
            else:
                PortSelector._get_names_from_list(device, DEVICES.values())
            return_list.append((port.device, device))
        return return_list

    @staticmethod
    def get_port_of(device_key: str) -> str | None:
        if device_key not in DEVICES:
            return None
        devices = PortSelector.get_devices([DEVICES[device_key]])
        if not devices:
            return None
        port, _ = devices[0]
        return port


class USBConnection:
    port: str
    baud_rate: int
    add_line_break: bool
    ser: Serial | None

    def __init__(self, port: str, baud_rate: int, add_line_break: bool = False) -> None:
        self.port = port
        self.baud_rate = baud_rate
        self.add_line_break = add_line_break
        self.ser = None

    def __enter__(self) -> USBConnection:
        self.ser = Serial(self.port, self.baud_rate, timeout=1)
        self.ser.flush()
        return self

    def __exit__(self, *_: Any) -> None:
        if self.ser is not None:
            self.ser.close()
        self.ser = None

    def listen(self, timeout: float = 0.01, bytes=False) -> None:
        if self.ser is None:
            raise Exception('Port is closed. Use "with" block to access this interface.')
        time.sleep(timeout)
        while self.ser.inWaiting() > 0:
            # read the bytes and convert from binary array to ASCII
            data_str = self.ser.read(self.ser.inWaiting())
            if bytes:
                data_str = str(bin(int.from_bytes(data_str)))[2:].rjust(8, '0')
            else:
                data_str = data_str.decode('ascii')
            print(f'Recieving: {data_str}')
            time.sleep(timeout)

    def write(self, message: str) -> None:
        if self.ser is None:
            raise Exception('Port is closed. Use "with" block to access this interface.')
        if self.add_line_break:
            message = message + '\n'
        s = str.encode(message)
        self.ser.write(s)
        print(f'Just wrote {s!r}')
        time.sleep(0.01)


def main() -> None:
    dev = USBConnection(port="COM4", baud_rate=9600)
    with dev:
        while True:
            dev.write(input('Command: '))
            dev.listen(0.1)


if __name__ == '__main__':
    main()
