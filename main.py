# Hardware interface classes
from pythion.connections import PicoOutput
from pythion.connections import LinearCalibration

# GUI Classes
from pythion import OutputComponent
from pythion import MainWindowComponent


def on_invalid() -> None:
    print('Invalid!')


# Define hardware intefaces:
MAX_VOLTAGE = 370
port = 'COM3'
cal = LinearCalibration(350)
pico = PicoOutput(port=port, calibration=cal, voltage_limit=MAX_VOLTAGE)
pico.add_invalid_output_handler(on_invalid)

# Setup GUI
with pico:
    pico.target = 0  # Initialize voltage at 0

    win = MainWindowComponent()
    # output_component1 = OutputComponent(MAX_VOLTAGE, pico, parent=win)
    output_component2 = OutputComponent(400, pico, parent=win)
    win.add_children(output_component2)
    win.run()
