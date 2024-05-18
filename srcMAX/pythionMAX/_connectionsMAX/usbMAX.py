from __future__ import annotations
import logging
from typing import Iterable, Any, Self
from enum import Enum
from serial.tools import list_ports  # type: ignore
from serial import Serial  # type: ignore
from dataclasses import dataclass


logger = logging.getLogger('pythion')


class USBConnectionException(Exception):
    pass


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
# to the manifacturer of the USB serial conversion chip, rather than the actual power supply.
DEVICES = {
    'pico': USBDevice(0x2e8a, 0x0005, 'Raspberry PI', 'Pico'),
    'rs': USBDevice(0x0416, 0x5011, 'RS', '3005P'),
    'rbd': USBDevice(0x0403, 0x6001, 'RBD', 'Picoammeter'),
    'CAEN': USBDevice(0x21E1, 0x0003, 'CAEN', 'R1419ET')
}


class ConnectionSettings(Enum):
    """
    These connection settings are for example used by PortSelector.get_options_list below.
    They correspond to the following options:
          - (AUTO)      Return only the first match, if any. Can be used when only one device of type is connected.
          - (MATCH)     Return all devices matching the type.
          - (RECOMMEND) Return all devices, but add a recommendation to the matches.
          - (ANY)       Return all devices.
    """
    AUTO = 1
    MATCH = 2
    RECOMMEND = 3
    ANY = 4


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
            if isinstance(port.vid, int):
                device = USBDevice(port.vid, port.pid)
                if products is not None:
                    if not PortSelector._get_names_from_list(device, products):
                        continue
                else:
                    PortSelector._get_names_from_list(device, DEVICES.values())
                return_list.append((port.device, device))
        return return_list

    @staticmethod
    def get_options_list(device_key: str | None, option: ConnectionSettings) -> dict[str, str]:
        """
        To be used, for example, with a USB selection dropdown menu. Returns a dictionary with
        all matching devices as entries, whose key is the COM port and value is a presentation
        string. The result will be formatted in accordance to the ConnectionSetting options.
        """
        device = DEVICES.get(device_key)
        if device is None:
            option = ConnectionSettings.ANY

        if option != ConnectionSettings.ANY:
            device_list = [device] if device else None
            ret = {port: str(dev) for port, dev in PortSelector.get_devices(device_list)}

        if option == ConnectionSettings.ANY or option == ConnectionSettings.RECOMMEND:
            all = {port: str(device) for port, device in PortSelector.get_devices()}
            if option == ConnectionSettings.RECOMMEND:
                for port, str in all.items():
                    if port in ret:
                        all[port] = str + ' (recommended)'
            ret = all

        if option == ConnectionSettings.AUTO and len(ret) > 0:
            key, value = next(ret.items())
            ret = {key: value}
        return ret

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
    port: str | None
    baud_rate: int
    add_line_break: bool
    ser: Serial | None

    def __init__(self, port: str, baud_rate: int, eol_char: str | None = None, xon_xoff: bool | None = False):
        """
        The port need not be set at the time of initialization, but it must have a value by the time
        __enter__ is called!
        """
        self.port = port
        self.baud_rate = baud_rate
        self.eol_char = eol_char
        self.ser = None
        self.xon_xoff = xon_xoff

    def __enter__(self) -> Self:
        # Serial default configuration:
        #    Byte size: 8
        #       Parity: None
        #    Stop bits: 1
        # Flow control: None (xonxoff = False)
        # If you need any other config, please implement that
        # yourself by adding parameters to the class constructor and use them here
        if self.port is None:
            return

        self.ser = Serial(self.port, self.baud_rate, timeout=5, xonxoff=self.xon_xoff)
        self.ser.flush()
        try:
            super().__enter__()  # type: ignore
        except AttributeError:
            pass
        logger.info(f'USBConnection:  Successfully opened USB connection on port {self.port}')
        return self

    def __exit__(self, *args: Any) -> None:
        if self.ser is not None:
            self.ser.close()
        try:
            super().__exit__(*args)  # type: ignore
        except AttributeError:
            pass
        logger.info(f'USBConnection:  Successfully closed connection on port {self.port}')

    def write(self, message: str) -> None:
        self._check_port_open()
        assert self.ser is not None
        if self.eol_char:
            message = message + self.eol_char
        s = str.encode(message)
        self.ser.write(s)
        logger.debug(f'USBConnection:  Written {s!r} on port {self.port}')

    def read_newlines(self, max_lines: int | None = None) -> list[str]:
        """
        Important: only call this method if you're expecting a steady stream on lines,
        otherwise, this method might lock the main thread.

        Returns a generator that flushes the new lines in the buffer and returns them one by one.

        This blogpost (https://be189.github.io/lessons/14/asynchronous_streaming.html) describes why
        reading with read_all on a windows machine could be problematic, hence the read_until loop.
        However, this reading is done in a completely synchronous fashion, so the caller needs to be
        responsible of handling the async business (i.e. not just call this method on repeat in a while
        loop)
        """
        self._check_port_open()
        assert self.ser is not None
        data: list[bytes] = []
        logger.debug(f'USBConnection:  Start reading on port {self.port}')
        while self.ser.in_waiting > 0:
            # Could it happen that this while loop never exit if the stream writes fast enough?
            # Only one way to find out!
            # For that reason, a max_lines argument is also passed
            line = self.ser.read_until()
            logger.debug(f'USBConnection:  Read line: {line!r}')
            data.append(line)
            if max_lines is not None and len(data) > max_lines:
                break
        # Decode after looping is finished, to reduce risk of getting stuck in loop
        return [b.decode() for b in data]

    def _check_port_open(self) -> None:
        if self.ser is None:
            logger.exception(f'USBConnection:  Port {self.port} is closed. Use "with" block to access this interface.')


def main() -> None:
    dev = USBConnection(port="COM5", baud_rate=57600, eol_char='\r\n')
    with dev:
        while True:
            com = input('Command: ')
            if com == "read":
                for line in dev.read_newlines():
                    print(line.strip())
            else:
                dev.write(com)


def find_ports(key: str):
    device = DEVICES[key]
    matches = PortSelector.get_devices([device])
    for port, device in matches:
        print(port, device)


if __name__ == '__main__':
    find_ports('rs')
