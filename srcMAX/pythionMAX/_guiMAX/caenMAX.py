from __future__ import annotations
import logging
import copy
#import time

from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from srcMAX.pythionMAX._layoutMAX.CAEN.ui_main_caen_2 import Ui_CAEN
from srcMAX.pythionMAX._connectionsMAX.output_interfaceMAX import OutputInterface #TODO Try to see if the output interface can be modified for this purpouse
from srcMAX.pythionMAX._guiMAX.connect_buttonMAX import ConnectButton
from srcMAX.pythionMAX._connectionsMAX.usbMAX import USBConnection

###INTERFACE FILE

logger = logging.getLogger('pythion')

class CAEN(QWidget, Ui_CAEN, ConnectButton):
    valueChanged: pyqtSignal = pyqtSignal(float)
    def __init__(self, *, 
                 interface = OutputInterface,
                 parent: QWidget | None = None, 
                 name: str | None = None,
                 unit: str | None = None
                 ):
        #Boilerplate init.
        super().__init__(parent)
        self.setupUi(self) #type: ignore
        #connectbutton init.
        super(Ui_CAEN, self).__init__()
        #custom init.
        self.name = name
        self.interface = interface
        self.unit = unit
        self.configure()
        self.CH0 = CEANChannel(chno=0)
        self.CH1 = CEANChannel(chno=1)
        self.CH2 = CEANChannel(chno=2)
        self.CH3 = CEANChannel(chno=3)
        self.CH0.set_defult()
        self.CH1.set_defult()
        self.CH2.set_defult()
        self.CH3.set_defult()

        self.defultBPparams = { #should not be modified
            'BDILK': False,
            'BDILKM': False,
            'BDCTR': False,
            'BDTERM': False,
            'BDALARM': 0
        }
        self.BPparams = copy.deepcopy(self.defultBPparams) #this is the one that should be modified

        self.defultBPstatus = { #should not be modified
            'CH 00': False,
            'CH 01': False,
            'CH 02': False,
            'CH 03': False,
            'PW FAIL': False,
            'OVP': False,
            'HVCKFAIL': False
        }
        self.BPstatus = copy.deepcopy(self.defultBPstatus) #this is the one that should be modified

    def configure(self) -> None: ###TODO
        label = self.name if self.name else 'CAEN'
        label = label + (f' [{self.unit}]' if self.unit else '')
        self.label = label
        #self.interface.add_input_handler(self._on_new_value) ### WRITE add_input_handler
        
        ### Setting up comms ###Need to send one inital message for return string to be corrext
        #self.interface._write(str.encode("$BD:00,CMD:MON,PAR:BDNAME"))

        pass

    def _activate(self) -> None: ###TODO
        """
        Called just after CAEN connection has been established.
        """
        ### ALL CHANNELS
        self.ON_BTN.setEnabled(True)
        self.OFF_BTN.setEnabled(True)

        ### CHANNEL PARAMETERS
        self.CP_table.setEnabled(True)

        ### SIMPLE CHANNEL CONTROLL
        self.channel_number_box.setEnabled(True)
        self.pushButton_7.setEnabled(True)
        self.vset_slide.setEnabled(True)
        self.vset_slide_2.setEnabled(True)
        #self.lineEdit.setEnabled(True)
        #self.lineEdit_2.setEnabled(True)

        ### BOARD PARAMETER CONFIGURATION
        self.comboBox.setEnabled(True)
        self.lineEdit_3.setEnabled(True)
        self.pushButton_8.setEnabled(True)

        ### CHANNEL PARAMETER CONFIG
        self.spinBox.setEnabled(True)
        self.comboBox_2.setEnabled(True)
        self.lineEdit_4.setEnabled(True)
        self.pushButton_5.setEnabled(True)

        #¤¤ BOARD CONTROLL
        self.pushButton_6.setEnabled(True)
        self.tableWidget_3.setEnabled(True)
        self.tableWidget_4.setEnabled(True)

        ### CHANNEL STATUS
        self.tableWidget_2.setEnabled(True)

        self._update_graphics()

    def _deactivate(self) -> None: ###TODO
        """
        Called just after CAEN connection has been destroyed.
        """
        ### ALL CHANNELS
        self.ON_BTN.setEnabled(False)
        self.OFF_BTN.setEnabled(False)

        ### CHANNEL PARAMETERS
        self.CP_table.setEnabled(False)

        ### SIMPLE CHANNEL CONTROLL
        self.channel_number_box.setEnabled(False)
        self.pushButton_7.setEnabled(False)
        self.vset_slide.setEnabled(False)
        self.vset_slide_2.setEnabled(False)
        #self.lineEdit.setEnabled(False)
        #self.lineEdit_2.setEnabled(False)

        ### BOARD PARAMETER CONFIGURATION
        self.comboBox.setEnabled(False)
        self.lineEdit_3.setEnabled(False)
        self.pushButton_8.setEnabled(False)

        ### CHANNEL PARAMETER CONFIG
        self.spinBox.setEnabled(False)
        self.comboBox_2.setEnabled(False)
        self.lineEdit_4.setEnabled(False)
        self.pushButton_5.setEnabled(False)

        #¤¤ BOARD CONTROLL
        self.pushButton_6.setEnabled(False)
        self.tableWidget_3.setEnabled(False)
        self.tableWidget_4.setEnabled(False)

        ### CHANNEL STATUS
        self.tableWidget_2.setEnabled(False)
        pass

    def _set_value_without_graphics(self, param, val) -> None: ###TODO
        pass


    def updateCPtable(self, ch: CEANChannel) -> None:
        keyList = list(ch.params.keys())
        for i, key in enumerate(keyList):
            logger.debug(f"updateCPtable: ({ch.get_ch()},{i})")
            self.CP_table.item(i, ch.get_ch()).setText(str(ch.params[key]))
            
    def updateCStable(self, ch: CEANChannel) -> None:
        keyList = list(ch.status.keys())
        for i, key in enumerate(keyList):
            logger.debug(f"updateCPtable: ({ch.get_ch()},{i})")
            self.tableWidget_2.item(i, ch.get_ch()).setText('')
            color = QBrush(QColor("Red")) if bool(ch.status[key]) else QBrush(QColor("yellowgreen"))
            self.tableWidget_2.item(i, ch.get_ch()).setBackground(color)

    def updateBPlist(self) -> None:
        self.tableWidget_3.item(0, 0).setText('NO')     if not self.BPparams['BDILK']  else self.tableWidget_3.item(0, 0).setText('YES')
        self.tableWidget_3.item(1, 0).setText('CLOSED') if not self.BPparams['BDILKM'] else self.tableWidget_3.item(1, 0).setText('OPEN')
        self.tableWidget_3.item(2, 0).setText('REMOTE') if not self.BPparams['BDCTR']  else self.tableWidget_3.item(2, 0).setText('LOCAL')
        self.tableWidget_3.item(3, 0).setText('OFF')    if not self.BPparams['BDTERM'] else self.tableWidget_3.item(3, 0).setText('ON')
        self.tableWidget_3.item(4, 0).setText(f'{00000}') #xxxxx is a int that needs to be converted to a bool and i assume that it is the digit sum that should be here

    def updateBAlist(self) -> None:
        keyList = list(self.BPstatus.keys())
        for i, key in enumerate(keyList):
            color = QBrush(QColor("Red")) if bool(self.BPstatus[key]) else QBrush(QColor("yellowgreen"))
            self.tableWidget_4.item(i, 0).setBackground(color)
            self.tableWidget_4.item(i, 0).setText('')
        pass

    def updateBPconfig(self) -> None:
        parSelected = str(self.comboBox.currentText())
        if parSelected == '_':
            pass
        else:
            self.lineEdit_3.text(self.BPparams[parSelected])
            self.textBrowser.clear()
            self.textBrowser.text("Info box is \nnot yet implemented")

    def updateCPconfig(self) -> None:
        chSelected = self.spinBox.value()
        parSelected = str(self.comboBox_2.currentText())
        if parSelected == '_':
            pass
        else:
            match chSelected:
                case 0:
                    self.lineEdit_4.text(self.CH0.params[parSelected])
                case 1:
                    self.lineEdit_4.text(self.CH1.params[parSelected])
                case 2:
                    self.lineEdit_4.text(self.CH2.params[parSelected])
                case 3:
                    self.lineEdit_4.text(self.CH3.params[parSelected])
                case _:
                    logger.exception(f"updateCPconfig:     How did you get here? how did you select channel {chSelected}?")
            self.textBrowser.clear()
            self.textBrowser.text("Info box is \nnot yet implemented")
        pass

    def _update_graphics(self) -> None: ###TODO
        for channel in [self.CH0, self.CH1, self.CH2, self.CH3]:
            self.updateCPtable(channel)
            self.updateCStable(channel)
        self.updateBPlist()
        self.updateBAlist()

    def set_value_and_update(self) -> None: ###TODO
        self._update_graphics()
        pass

    def __str__(self) -> str: ###Likley unecessary
        pass

    @pyqtSlot(float, bool)
    def setvalue(self, ch): ### THIS IS THE BIG ONE
        pass



    def __exit__(self, *args) -> None: ###Likley compleate
        super().__exit__(self, *args)   

class CEANChannel():
    def __init__(
                self, *,
                chno : int, 
                IMON: float | None = None,
                IMRANGE: str | None = None,
                ISET: float | None = None,
                MAXV: int | None = None,
                PDWN: str | None = None,
                POL: str | None = None,
                RDW: int | None = None,
                RUP: int | None = None,
                STAT: int | None = None,
                TRIP: float | None = None,
                VMON: float | None = None,
                VSET: int | None = None
                ):

        self.isON: bool = False
        
        self.defult_params = {
            'IMON': 000.00,
            'IMRANGE': 'HIGH',
            'ISET': 030.00,
            'MAXV': 550.00,
            'PDWN': 'KILL',
            'POL': '+',
            'RDW': 050.00,
            'RUP': 050.00,
            'STAT': '00001',
            'TRIP': 0010.00,
            'VMON': 000.00,
            'VSET' : 000.00
        }

        self.defult_status = {
            'ON': False,
            'RUP': False,
            'RDW': False,
            'OVC': False,
            'OVV': False,
            'UNV': False,
            'MAXV': False,
            'TRIP': False,
            'OVP': False,
            'OVT': False,
            'DIS': False,
            'KILL': False,
            'ILK': False,
            'NOCAL': False
        }
    
        self.params = {
            'IMON': IMON,
            'IMRANGE': IMRANGE,
            'ISET': ISET,
            'MAXV': MAXV,
            'PDWN': PDWN,
            'POL': POL,
            'RDW': RDW,
            'RUP': RUP,
            'STAT': STAT,
            'TRIP': TRIP,
            'VMON': VMON,
            'VSET' : VSET
        }

        self.ch = chno
        self.status = copy.deepcopy(self.defult_status)

    def get_val(self, key: str) -> str:
        return self.params[f'{key}']
    
    def set_val(self, param: str, val: str | float) -> None:
        self.params[param] = val

    def get_ch(self) -> int:
        return self.ch
    
    def set_defult(self) -> None:
        self.params = copy.deepcopy(self.defult_params)

    def clear_status(self) -> None:
        self.status = copy.deepcopy(self.defult_status)

if __name__ == '__main__':
    pass
