from PyQt5.QtWidgets import QPushButton
from srcMAX.pythionMAX._connectionsMAX.usbMAX import USBConnection
from contextlib import AbstractContextManager
import logging
from typing import Self, Any
logger = logging.getLogger('pythion')


class ConnectButton():
    connectBtn: QPushButton
    interface: AbstractContextManager
    _connected: bool
    _in_context_manager: bool

    def __init__(self):
        self.connectBtn.setText('Connect')
        self._connected = False
        self._in_context_manager = False
        self.connectBtn.clicked.connect(self._on_connect_pressed)  # type: ignore

    def _on_connect_pressed(self) -> None:
        if not self._connected:
            # Connect button pressed, Let's try to conncet!
            if not self._in_context_manager:
                logger.warning('ConnectButton:  Attempted to connect without using a context manager!')
                return
            if isinstance(self.interface, USBConnection):
                if self.interface.port is None:
                    self._select_port_and_retry()
            self.interface.__enter__()
            self._connected = True
            self._activate()
            logger.debug('ConnectButton:  Connected.')
            self.connectBtn.setText('Disconnect')
        else:
            self._deactivate()
            self.interface.__exit__(None, None, None)
            self._connected = False
            self._value_set = False
            logger.debug("ConnectButton:  Disconnected successfully by user's request.")
            self.connectBtn.setText('Connect')

    def _activate():  # Would be marked abstract if it wasn't for metaclass complications...
        pass

    def _deactivate():  # Would be marked abstract if it wasn't for metaclass complications...
        pass

    def _select_port_and_retry(self):
        logger.waring('ConnectButton:  Port selection not implemented!')

    def __enter__(self, *args) -> Self:
        self._in_context_manager = True
        return self

    def __exit__(self, *args: Any):
        logger.debug("ConnectButton:  Disconnected successfully by termination.")
        self._in_context_manager = False
        self.interface.__exit__(*args)
