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
port_rs = PortSelector.get_port_of('rs')

# Pico
MAX_VOLTAGE_PICO = 300
calibration_pico = LinearCalibration(350)
port_pico = PortSelector.get_port_of('pico')

assert port_rs is not None
assert port_pico is not None

rs = RS3000Output(port=port_rs, voltage_limit=MAX_VOLTAGE_RS)
pico = PicoOutput(port=port_pico, calibration=calibration_pico, voltage_limit=MAX_VOLTAGE_PICO)
rs.add_invalid_output_handler(on_invalid)

# Setup GUI
with rs, pico:
    rs.target = 0  # Initialize voltage at 0
    pico.target = 0

    win = MainWindowComponent()
    output_component1 = OutputComponent(MAX_VOLTAGE_RS, rs, parent=win)
    output_component2 = OutputComponent(MAX_VOLTAGE_PICO, pico, parent=win)
    win.add_children(output_component1, output_component2)
    win.run()
