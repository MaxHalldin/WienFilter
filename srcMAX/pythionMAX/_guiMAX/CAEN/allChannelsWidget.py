from __future__ import annotations
import logging

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from srcMAX.pythionMAX._layoutMAX.CAEN.ui_all_channels import Ui_Form as Ui_AllChannels
from srcMAX.pythionMAX._guiMAX.connect_buttonMAX import ConnectButton

logger = logging.getLogger('pythion')

class AllChannels(QWidget, ConnectButton, Ui_AllChannels):
    def __init__(self, *,
                 max_value = int,
                 interface = None, #TODO create interface
                 parent: QWidget | None = None, 
                 name: str | None = None,
                 unit: str | None = None #unsure if needed 
                 ):
        # Boilerplate initialization
        super().__init__(parent)
        self.setupUi(self)
        # Custom initialization
        super(Ui_AllChannels, self).__init__()
        self.interface = interface
        self.max_value = max_value
        self.name = name
        self.unit = unit    #unsure if needed 
        self._value_set = False
        label = name if name else 'AllChannels'
        self.label = label + (f' [{unit}]' if unit else '') #unsure what this does and if needed. Think if is important if you try to add multiple widgets.
        self.configure()

    def configure(self) -> None:
        self.nameLabel.setText(self.label)
        #May need some config som state of the buttons

    def __str__(self):
        return self.label
    
    #I'm somewhat unsure about what these buttons do :/
    @pyqtSlot(bool)
    def vset_button(self) -> None:
        """
        TODO
        """
        if not self._connected:
            logger.warning("AllChannels:         Attempted to ??? vset without connection")
            return
        else:
            self._() ### 
    
    @pyqtSlot(bool)
    def iset_button(self) -> None:
        """
        TODO
        """
        if not self._connected:
            logger.warning("AllChannels:         Attempted to ??? iset without connection")
            return
        else:
            self._() ### 

    @pyqtSlot(bool)
    def on_button(self) -> None:
        """
        TODO
        """
        if not self._connected:
            logger.warning("AllChannels:         Attempted to turn on without connection")
            return
        else:
            self._() ### 

    @pyqtSlot(bool)
    def off_button(self) -> None:
        """
        TODO
        """
        if not self._connected:
            logger.warning("AllChannels:         Attempted to turn off without connection")
            return
        else:
            self._() ### 

    def __exit__(self, *args):
        super().__exit__(self, *args)