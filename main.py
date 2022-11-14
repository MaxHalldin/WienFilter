# Hardware interface classes
from pythion.connections import MockOutput, PicoOutput
from pythion.connections import LinearCalibration

# GUI Classes
from pythion import OutputComponent
from pythion import MainWindowComponent

# Define hardware intefaces:
# MAX_VOLTAGE = 10
# port = 'COM3'
# cal = LinearCalibration(10)
# pico = PicoOutput(port, cal, MAX_VOLTAGE)

mock = MockOutput()
# Setup GUI

with mock:
    #pico.target = 0 # Initialize voltage at 0
    win = MainWindowComponent()
    # output_component1 = OutputComponent(MAX_VOLTAGE, pico, parent=win)
    output_component2 = OutputComponent(350, mock, parent=win)
    win.add_children(output_component2)
    win.run()