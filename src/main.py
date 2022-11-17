# Hardware interface classes
from pythion.connections import RS3000Output, PicoOutput, PortSelector, LinearCalibration, MockOutput, Output

# GUI Classes
from pythion import OutputComponent
from pythion import MainWindowComponent

PICO = True
RS = True

# Define hardware intefaces:
# RS 3005P
MAX_VOLTAGE_RS = 5
MAX_CURRENT_RS = 50
MODE_RS = RS3000Output.PowerOptions.CURRENT
INPUT_MAX_RS = MAX_VOLTAGE_RS if MODE_RS == RS3000Output.PowerOptions.VOLTAGE else MAX_CURRENT_RS

# Pico
MAX_VOLTAGE_PICO = 300
CALIBRATION_PICO = LinearCalibration(350)


def on_invalid() -> None:
    print('Invalid!')


port_pico = PortSelector.get_port_of('pico')
port_rs = PortSelector.get_port_of('rs')


def configure_pico() -> PicoOutput:
    assert port_pico is not None
    return PicoOutput(port=port_pico, calibration=CALIBRATION_PICO, voltage_limit=MAX_VOLTAGE_PICO)


def configure_rs() -> RS3000Output:
    assert port_rs is not None
    return RS3000Output(port=port_rs,
                        voltage_limit=MAX_VOLTAGE_RS,
                        current_limit=MAX_CURRENT_RS,
                        mode=MODE_RS)


pico: Output
rs: Output
if PICO:
    pico = configure_pico()
else:
    pico = MockOutput()
if RS:
    rs = configure_rs()
else:
    rs = MockOutput()

# Setup GUI
with rs, pico:
    pico.target = 0

    win = MainWindowComponent()
    pico_component = OutputComponent(MAX_VOLTAGE_PICO, pico, parent=win)
    rs_component = OutputComponent(INPUT_MAX_RS, rs, parent=win)
    win.add_children(pico_component, rs_component)
    win.run()
