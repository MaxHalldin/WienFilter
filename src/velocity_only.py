# Hardware interface classes
from pythion.connections import PicoOutput, LinearCalibration, PortSelector

# GUI Classes
from pythion import Output, MainWindow

# Magnet output
port = PortSelector.get_port_of('pico')
assert port

cal = LinearCalibration(350)
output_device = PicoOutput(
    port=port,
    calibration=cal,
    voltage_limit=100
)

# Setup GUI
with output_device:
    win = MainWindow(high_resolution=False)
    output_component = Output(
        max_value=100,
        interface=output_device,
        parent=win.main_widget(),
        name="Velocity filter",
        unit="V"
    )
    win.add_children(output_component)
    win.run()
