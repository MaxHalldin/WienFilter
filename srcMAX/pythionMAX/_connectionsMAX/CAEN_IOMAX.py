from __future__ import annotations
from typing import Self
import logging
import re

logger = logging.getLogger('pythion')

from srcMAX.pythionMAX._connectionsMAX.calibrationMAX import LinearCalibration, Calibration
from srcMAX.pythionMAX._connectionsMAX.output_interfaceMAX import OutputInterface
from srcMAX.pythionMAX._connectionsMAX.usbMAX import USBConnection
#from srcMAX.pythionMAX._connectionsMAX.buffer_inputMAX import BufferInput

class CAENOutput(OutputInterface, USBConnection):
    """
    Specialization of the Output class for a CAEN R1419ET HV power supply.
    
    Each parameter

    PARAMETERS:
        port: str                   - The COM port which the power supply is connected to. 
    """

    def __init__(self, *, 
                 port: str | None,
                 calibration: Calibration | None = None,
                 bd: str | None = 0
                 ):
        
        self.bd = bd
        BAUD_RATE = 9600
        USBConnection.__init__(
            self,
            port=port,
            baud_rate=BAUD_RATE,
            eol_char= ' \r \n',
            xon_xoff=True
            )
        OutputInterface.__init__(
            self,
            calibration = calibration
        )

    def __enter__(self)-> Self:
        super().__enter__()
        return self

    def parse_response_string(self, msg:str) -> list[float|str] | None:
        try:
            original_message: str = msg.strip()
            if not bool(re.match(r'^#BD:\d{2},\w{2,3}:\w{2,3}(|(,VAL:(\S|(\w+\.*\w+;?){1,4})))$', original_message)): #regex101.com is a lifesaver
                logger.warning(f"CAENOutput:       Cannot interpret the line '{original_message}' as it doesn't fit pattern.")
                return None

            split_message: list[str] = original_message.split(',')
            msg_end: str = split_message[-1]

            if msg_end[-3:] == 'ERR':
                err_par: str = msg_end.split(':')[0]
                logger.warning(f"CAENOutput:       CAEN error. error parameter {err_par}. See documentation")
                return None
            
            if msg_end == 'CMD:OK':
                logger.debug(f"CAENOutput:         Interpreted {original_message} as OK")
                return None
            
            res: list[float|str] = msg_end[3:].split(';')
            for index, item in enumerate(res):
                if bool(re.match(r"^\d+\.*\d*", item)):
                    res[index] = int(item)
                elif bool(re.match(r"^\d+\.*\d*", item)):
                    res[index] = float(item)

            logger.debug(f"CAENOutput:         Interpreted {original_message} as OK, returned {res}")
            return res
            

        except (ValueError, AssertionError, IndexError):
            logger.warning(f"CAENOutput:       Unexpected error when the line '{msg.strip()}' was parsed.")
            return None

    def _write(self, msg: str) -> None:
        """
        Message is of shape " $BD:**,CMD:***,CH*,PAR:***,VAL:***.**\r \n"

            BD:         [0, 31]         | "board"       |   Should always be 0 if there are not multiple daisy chained CAEN devices. \n
            CDM:        {'MON', 'SET'}  | "command"     |   MON -> Monitor & SET -> set. \n
            CH:         [0, 3]          | "channel"     |   For the R1419ET CH_max = 3 for other hardware it might be 7. \n
            PAR:        {see init}      | "parameter"   |   See documentation for all possible, see init for all avaliable. \n
            VAL:        ###             | "value"       |   compatible numerical value.
        
        when MON: VAL = ''.

        """        
        self.write(msg)

    def makeMessage(self, cmd: str, ch: int | None = None, bd = 0, par = str, val = int | str | None) -> str:
            """
            Constructs a message to be sent over the bus to CAEN.
            """
            message = '$BD:'
            parlist = ['VSET', 'VMIN', 'VMAX', 'VDEC', 'VMON', 
                    'ISET', 'IMIN', 'IMAX', 'ISDEC', 'IMON', 'IMRANGE', 'IMDEC',
                    'MAXV', 'MVMIN', 'MVMAX', 'MVDEC', 
                    'RUP', 'RUPMIN', 'RUPMAX', 'RUPDEC', 
                    'RDW', 'RDWMIN', 'RDWMAX', 'RDWDEC',
                    'TRIP', 'TRIPMIN', 'TRIPMAX', 'TRIPDEC',
                    'PDDW', 'POL', 'STAT'#, 'ZSDTC', 'ZCADJ'    ### These are not avalible on the R1419ET
                    ]

            #
            message = message + '0' + str(bd) + ',CMD:'

            #
            match cmd:
                case 'MON':
                    message = message + 'MON'
                case 'SET':
                    message = message + 'SET'
        
            #
            if ch is not None:
                message + message + str(ch) + ','
        
            #
            if par not in parlist:
                logger.exception(f"CAEN:         Invalid parameter {par}.")
            else:
                message = message + 'PAR:' + str(par) + ','
        
            #
            if val is not None:
                message = message + str(val)
            return message 