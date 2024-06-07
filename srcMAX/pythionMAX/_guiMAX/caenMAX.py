from __future__ import annotations
import logging
import copy

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QWidget
from srcMAX.pythionMAX._layoutMAX.CAEN.ui_main_caen_2 import Ui_CAEN
from srcMAX.pythionMAX._connectionsMAX.output_interfaceMAX import OutputInterface #TODO Try to see if the output interface can be modified for this purpouse
from srcMAX.pythionMAX._guiMAX.connect_buttonMAX import ConnectButton
from srcMAX.pythionMAX._connectionsMAX.CAEN_IOMAX import CAENOutput

###INTERFACE FILE

logger = logging.getLogger('pythion')

class CAEN(QWidget, Ui_CAEN, ConnectButton):
    
    def __init__(self, *, 
                 interface = OutputInterface | CAENOutput,
                 rate: int,
                 parent: QWidget | None = None,
                 unit: int | None = 0
                 ):
        #Boilerplate init.
        super().__init__(parent)
        self.setupUi(self) #type: ignore
        #connectbutton init.
        super(Ui_CAEN, self).__init__()
        #custom init.
        self.interface = interface
        self.rate = rate
        self.unit = unit
        self.timer = QTimer(self) ###WILL TRY THIS FIRST. IF TOO SLOW: TRY Qtrhead
        self.timer.setInterval(1000)
        self.configure()

        self.CH0 = CEANChannel(chno=0)
        self.CH1 = CEANChannel(chno=1)
        self.CH2 = CEANChannel(chno=2)
        self.CH3 = CEANChannel(chno=3)
        self.CH0.set_defult()
        self.CH1.set_defult()
        self.CH2.set_defult()
        self.CH3.set_defult()
        self.CHlist = [self.CH0, self.CH1, self.CH2, self.CH3]

        self.defultBPparams = { #should not be modified
            'BDILK': False,
            'BDILKM': False,
            'BDCTR': False,
            'BDTERM': False,
            'BDALARM': '0'
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

        self.editableCP: list[str] = ['VSET', 'ISET', 'MAXV', 'RUP', 'RDW', 'TRIP', 'DPWN', 'IMRANGE']
        self.intCP: list[str] = ['MAXV', 'RUP', 'RDW']
        self.floatCP: list[str] = ['VSET', 'ISET', 'TRIP'] 
        self.strCP: list[str] = ['DPWN', 'IMRANGE']

    def configure(self) -> None:
        self.ON_BTN.clicked.connect(self.AllCHON)
        self.OFF_BTN.clicked.connect(self.AllCHOFF)
        self.pushButton_6.clicked.connect(self.clearBoardControllAlarms)
        self.comboBox.currentTextChanged.connect(self.BPComboChange)
        self.comboBox_2.currentTextChanged.connect(self.CPComboChanche)
        self.spinBox.valueChanged.connect(self.CPComboChanche)
        self.pushButton_8.clicked.connect(self.setBP)
        self.pushButton_5.clicked.connect(self.setCP)
        self.pushButton_7.clicked.connect(self.OneCHONOFF)
        self.channel_number_box.valueChanged.connect(self.SCC)
        self.vset_slide.valueChanged.connect(self.VSlideEvent)
        self.vset_slide_2.valueChanged.connect(self.ISlideEvent)
        self.timer.timeout.connect(self.AutoUpdate)

    def AllCHON(self) -> None:
        #self.allChannelsIsOn = True
        self.interface._write(bd = self.unit, cmd='SET', ch=4, par='ON')
        for i, ch in enumerate(self.CHlist):
            if self.interface._read_from_device()[i] == 'OK':
                ch.status['ON'] = True
                self.updateCStable(ch=ch)
        self.updateSCC()

    def AllCHOFF(self) -> None:
        #self.allChannelsIsOn = False
        self.interface._write(bd= self.unit, cmd='SET', ch=4, par='OFF')
        for i, ch in enumerate(self.CHlist):
            if self.interface._read_from_device()[i] == 'OK':
                ch.status['ON'] = False
                self.updateCStable(ch=ch)
        self.updateSCC()
    
    def OneCHONOFF(self) -> None:
        def changeLook(self) -> None:
            self.pushButton_7.setStyleSheet("background-color : lightblue") if self.pushButton_7.isChecked() else self.pushButton_7.setStyleSheet("background-color : lightgray")
        ch: int = self.channel_number_box.value()
        if self.CHlist[ch].status['ON'] == False:
            self.interface._write(bd = self.unit, cmd='SET', ch=ch, par='ON')
            self.CHlist[ch].status['ON'] = True
        else:
            self.interface._write(bd = self.unit, cmd='SET', ch=ch, par='OFF')
            self.CHlist[ch].status['ON'] = False
        changeLook(self)
        self.updateCStable(ch=self.CHlist[ch])
        self.updateSCC()

    def clearBoardControllAlarms(self) -> None:
        self.interface._write(bd= self.unit, cmd='SET', par='BDCLR')
        self.updateBAlist()

    def BPComboChange(self) -> None:
        self.updateBPconfig()

    def CPComboChanche(self) -> None:
        self.updateCPconfig()

    def setBP(self) -> None:
        text: str = self.lineEdit_3.text().upper()
        if text in ['OPEN', 'CLOSED']:
            self.interface._write(bd= self.unit, cmd='SET', par='BDILKM', val=text)
            self.lineEdit_3.setText(text)
            self.BPparams['BDILKM'] = True if text == 'OPEN' else False
        self.updateBPlist()

    def setCP(self) -> None:
        val: str = self.lineEdit_4.text().upper()
        ch: int = self.spinBox.value()
        par: str = self.comboBox_2.currentText()
        self.interface._write(bd= self.unit, cmd='SET', ch=ch, par=par, val=val)
        match par:
            case par if par in self.strCP:
                self.CHlist[ch].params[par] = val
            case par if par in self.intCP:
                self.CHlist[ch].params[par] = int(val)
            case par if par in self.floatCP:
                self.CHlist[ch].params[par] = float(val)
            case _:
                logger.exception(f"CAEN.setCP(): unknown parameter {val}")
        self.lineEdit_4.setText(val)
        self.updateCPtable(ch=self.CHlist[ch])

    def SCC(self) -> None:
        self.updateSCC()

    def VSlideEvent(self) -> None:
        ch: int = self.channel_number_box.value()
        newVal: float = self.vset_slide.sliderPosition()
        self.interface._write(bd=self.unit, cmd='SET', ch=ch, par='VSET', val=newVal)
        self.CHlist[ch].params['VSET'] = newVal
        self.updateSCC()
        #self.updateCPtable(ch=self.CHlist[ch])

    def ISlideEvent(self) -> None:
        ch: int = self.channel_number_box.value()
        newVal: float = self.vset_slide_2.sliderPosition()
        self.interface._write(bd=self.unit, cmd='SET', ch=ch, par='ISET', val=newVal)
        self.CHlist[ch].params['ISET'] = newVal
        self.updateSCC()
        #self.updateCPtable(ch=self.CHlist[ch])

    def _activate(self) -> None:
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
        ##self.lineEdit.setEnabled(True)
        ##self.lineEdit_2.setEnabled(True)

        ### BOARD PARAMETER CONFIGURATION
        self.comboBox.setEnabled(True)
        self.lineEdit_3.setEnabled(True)
        ##self.pushButton_8.setEnabled(True)

        ### CHANNEL PARAMETER CONFIG
        self.spinBox.setEnabled(True)
        self.comboBox_2.setEnabled(True)
        self.lineEdit_4.setEnabled(True)
        ##self.pushButton_5.setEnabled(True)

        #¤¤ BOARD CONTROLL
        self.pushButton_6.setEnabled(True)
        self.tableWidget_3.setEnabled(True)
        self.tableWidget_4.setEnabled(True)

        ### CHANNEL STATUS
        self.tableWidget_2.setEnabled(True)

        self._update_all_graphics()
        self.interface.start_sampling(self.rate)
        self.timer.start(1000) ###REMOMVE NUMBER AFTER TEST

    def _deactivate(self) -> None:
        """
        Called just after CAEN connection has been destroyed.
        """
        for ch in self.CHlist:
            ch.set_defult()
            ch.clear_status()
        self._update_all_graphics()
        self.timer.stop()
    
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

    def updateCPtable(self, ch: CEANChannel) -> None:
        keyList: list = list(ch.params.keys())
        for i, key in enumerate(keyList):
            logger.debug(f"updateCPtable: ({ch.get_ch()},{i})")
            self.CP_table.item(i, ch.get_ch()).setText(str(ch.params[key]))
            
    def updateCStable(self, ch: CEANChannel) -> None:
        keyList: list = list(ch.status.keys())
        err_col: str = "yellowgreen"
        chIndex: int = ch.get_ch()
        for i, key in enumerate(keyList):
            logger.debug(f"updateCPtable: ({chIndex},{i})")
            self.tableWidget_2.item(i, chIndex).setText(' ')
            color = QBrush(QColor(err_col)) if ch.status[key] else QBrush(QColor("white"))
            self.tableWidget_2.item(i, chIndex).setBackground(color)
            err_col = "Red"

    def updateBPlist(self) -> None:
        self.tableWidget_3.item(0, 0).setText('NO')     if not self.BPparams['BDILK']  else self.tableWidget_3.item(0, 0).setText('YES')
        self.tableWidget_3.item(1, 0).setText('CLOSED') if not self.BPparams['BDILKM'] else self.tableWidget_3.item(1, 0).setText('OPEN')
        self.tableWidget_3.item(2, 0).setText('REMOTE') if not self.BPparams['BDCTR']  else self.tableWidget_3.item(2, 0).setText('LOCAL')
        self.tableWidget_3.item(3, 0).setText('OFF')    if not self.BPparams['BDTERM'] else self.tableWidget_3.item(3, 0).setText('ON')
        self.tableWidget_3.item(4, 0).setText(f'{00000}') #xxxxx is a int that needs to be converted to a bool and i assume that it is the digit sum that should be here

    def updateBAlist(self) -> None:
        keyList: list = list(self.BPstatus.keys())
        for i, key in enumerate(keyList):
            color = QBrush(QColor("Red")) if self.BPstatus[key] else QBrush(QColor("white"))
            self.tableWidget_4.item(i, 0).setBackground(color)
            self.tableWidget_4.item(i, 0).setText('')
        pass

    def updateBPconfig(self) -> None:
        parSelected: str = str(self.comboBox.currentText())
        if parSelected == '_':
            self.textBrowser.setText("")
        else:
            keyList: list = list(self.BPparams.keys())
            self.lineEdit_3.setText(self.tableWidget_3.item(keyList.index(parSelected), 0).text())
            if parSelected == 'BDILKM':
                self.pushButton_8.setEnabled(True)
                self.textBrowser.setText("values: \nOPEN/CLOSED")
            else:
                self.textBrowser.setText("*Not editable*")

    def updateCPconfig(self) -> None:
        chSelected: int = self.spinBox.value()
        parSelected: str = str(self.comboBox_2.currentText())
        if parSelected == '_':
            self.textBrowser_2.setText("")
            self.pushButton_5.setEnabled(False)
        else:
            match chSelected:
                case 0:
                    self.lineEdit_4.setText(str(self.CH0.params[parSelected]))
                case 1:
                    self.lineEdit_4.setText(str(self.CH1.params[parSelected]))
                case 2:
                    self.lineEdit_4.setText(str(self.CH2.params[parSelected]))
                case 3:
                    self.lineEdit_4.setText(str(self.CH3.params[parSelected]))
                case _:
                    logger.exception(f"updateCPconfig:     How did you get here? how did you select channel {chSelected}?")
            if parSelected in self.editableCP:
                self.pushButton_5.setEnabled(True)
                self.textBrowser_2.setText("*Editable*")
            else:
                self.textBrowser_2.setText("*NOT editable*")
                self.pushButton_5.setEnabled(False)

    def updateSCC(self) -> None:
        ch: int = self.channel_number_box.value()
        def changeLook(self, ch:int) -> None:
            self.pushButton_7.setStyleSheet("background-color : lightblue") if self.CHlist[ch].status['ON'] else self.pushButton_7.setStyleSheet("background-color : white")
        self.lineEdit.setText("{:.2f}".format(self.CHlist[ch].params['VMON']))
        self.lineEdit_2.setText("{:.2f}".format(self.CHlist[ch].params['IMON']))
        self.vset_slide.setSliderPosition(int(self.CHlist[ch].params['VSET']))
        self.vset_slide_2.setSliderPosition(int(self.CHlist[ch].params['ISET']))
        changeLook(self, ch=ch)

    def _update_all_graphics(self) -> None:
        for channel in self.CHlist:
            self.updateCPtable(channel)
            self.updateCStable(channel)
        self.updateBPlist()
        self.updateBAlist()
        self.updateBPconfig()
        self.updateSCC()

    def __str__(self) -> str: ###Likley unecessary
        return f"R1419ET BD:0{self.unit}"

    ### This is the part for automatic updates.

    def __enter__(self, *args) -> None:
        try:
            super().__enter__(self, *args)
        except AttributeError:
            pass
        return self

    def __exit__(self, *args) -> None: ###Likley compleate
        try:
            super().__exit__(self, *args)   
        except AttributeError:
            pass

    def setSliders(self):
        """
        Do this here because otherwise the sliders emits a signal for ever frame where the value is different from what it was on the last frame,
        which would make SIMBA try to write to CAEN many times a second.
        """
        ch: int = self.channel_number_box.value()
        newIVal: float = self.vset_slide_2.sliderPosition()
        newVVal: float = self.vset_slide_2.sliderPosition()
        self.interface._write(bd=self.unit, cmd='SET', ch=ch, par='VSET', val=newVVal)
        self.interface._write(bd=self.unit, cmd='SET', ch=ch, par='ISET', val=newIVal)
        pass

    def MonitorContinuous(self) -> None:
        def GASCHparams(self) -> None:
            for parKey in self.CH0.params.keys():
                self.interface._write(bd = self.unit, cmd='MON', ch=4, par=parKey)
                tempParam: list = self.interface._read_from_device()
                self.CH0.params[parKey] = tempParam[0]
                self.CH1.params[parKey] = tempParam[1]
                self.CH2.params[parKey] = tempParam[2]
                self.CH3.params[parKey] = tempParam[3]

        def setCHSTAT(self, ch: CEANChannel) -> None:
            statStr: str = ch.params['STAT']
            statBitStr = "{:0>16b}".format(int(statStr))
            for i, key in enumerate(ch.status.keys()):
                ch.status[key] = False if statBitStr[i] == '0' else True

        def GASBDparams(self) -> None:
            for parKey in self.BDparams.keys():
                self.interface._write(bd = self.unit, cmd='MON', par=parKey)
                tempParam: str = self.interface._read_from_device()
                self.BDparams[parKey] = tempParam

        def setBDSTAT(self) -> None:
            statStr: str = self.BPparams['BDALARM']
            statBitStr = "{:0>16b}".format(int(statStr))
            for i, key in enumerate(self.BDstatus.keys()):
                self.BDstatus[key] = statBitStr[i]

        GASCHparams(self)
        for ch in self.CHlist:
            setCHSTAT(self, ch)
        GASBDparams(self)
        setBDSTAT(self)

    def AutoUpdate(self):
        self.setSliders()
        #self.MonitorContinuous()
        self._update_all_graphics()

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
