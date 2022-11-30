from pythion.gui import Output, MainWindow
from pythion.connections import RS3000Output, PortSelector

# Magnet output
port = PortSelector.get_port_of('rs')
assert port

output_device = RS3000Output(
    port=port,
    voltage_limit=5,
    current_limit=20,
    mode=RS3000Output.PowerOptions.CURRENT
)

# Setup GUI
win = MainWindow(high_resolution=True)
output_component = Output(
    max_value=20,
    interface=output_device,
    parent=win.main_widget(),
    name="Resistor current",
    unit="mA"
)
win.add_children(output_component)
with output_component:
    win.run()
