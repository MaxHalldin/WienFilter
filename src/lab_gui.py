# Hardware interface classes
from pythion.connections import PortSelector, RBDInput, RS3000Output, PicoOutput, LinearCalibration

# GUI Classes
from pythion import Output, Input, MainWindow, PlotStream

# Magnet output
port_magnet = PortSelector.get_port_of('rs')
assert port_magnet
magnet_output_device = RS3000Output(
    port=port_magnet,
    voltage_limit=5,
    current_limit=1000,
    mode=RS3000Output.PowerOptions.CURRENT
)

# Velocity filter
port_velocity = PortSelector.get_port_of('pico')
cal = LinearCalibration(350)
assert port_velocity
velocity_output_device = PicoOutput(
    port=port_velocity,
    calibration=cal,
    voltage_limit=300
)
# Input
port_rbd = PortSelector.get_port_of('rbd')
assert port_rbd
input_device = RBDInput(
    port=port_rbd,
    rbd_sample_rate=5,
    pull_rate=5,
    unit=RBDInput.CurrentUnit.NANO
)

# Setup GUI
with input_device, magnet_output_device, velocity_output_device:
    input_device.start_sampling(5)
    win = MainWindow(high_resolution=False)
    magnet_component = Output(
        max_value=30,
        interface=magnet_output_device,
        parent=win.main_widget(),
        name="Magnet",
        unit="mA"
    )
    velocity_filter_component = Output(
        max_value=300,
        interface=velocity_output_device,
        parent=win.main_widget(),
        name="Velocity Filter",
        unit="V"
    )
    input_component = Input(
        interface=input_device,
        name='Beam current',
        unit='nA',
        parent=win.main_widget()
    )
    plt_component = PlotStream(
        parent=win.main_widget(),
        input=input_device,
        timespan=10,
        fix_scale=False
    )
    win.add_children(magnet_component, velocity_filter_component, input_component, plt_component)
    win.run()
