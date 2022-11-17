# Hardware interface classes
from pythion.connections import RS3000Output, PicoOutput, PortSelector, LinearCalibration

# GUI Classes
from pythion import OutputComponent
from pythion import MainWindowComponent


def on_invalid() -> None:
    print('Invalid!')


# Define hardware intefaces:
# RS 3005P
MAX_VOLTAGE_RS = 30
MAX_CURRENT_RS = 50
MODE_RS = RS3000Output.PowerOptions.CURRENT
INPUT_MAX = MAX_VOLTAGE_RS if MODE_RS == RS3000Output.PowerOptions.VOLTAGE else MAX_CURRENT_RS

# Pico
MAX_VOLTAGE_PICO = 300
CALIBRATION_PICO = LinearCalibration(350)

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


rs = configure_rs()

# Setup GUI
with rs:
    rs.target = 0  # Initialize voltage at 0
    # pico.target = 0

    win = MainWindowComponent()
    output_component1 = OutputComponent(INPUT_MAX, rs, parent=win)
    # output_component2 = OutputComponent(MAX_VOLTAGE_PICO, pico, parent=win)
    win.add_children(output_component1)
    win.run()
