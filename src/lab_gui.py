# Hardware interface classes
from pythion.connections import PortSelector, RBDInput, RS3000Output, PicoOutput, LinearCalibration
import numpy as np
# GUI Classes
from pythion import Output, Input, MainWindow, PlotStream, GridSearch


PORT_RBD = 'COM0'
# Lab GUI parameters, to be read from config file!
#   Device setting params
MAGNETCONTROL_MAXCURRENT = 3000  # mA
VELOCITYCONTROL_MAXVOLTAGE = 300  # V
CURRENT_SAMPLERATE = 10  # Hz
CURRENT_PULLRATE = 5  # Hz
CURRENTGRAPH_REFRESHRATE = 5  # Hz
#   Grid search params
MAGNET_SETTIME = 1.5  # s
VELOCITY_SETTIME = 1.5  # s
MEASURING_TIME = 0.5  # s
MAGNET_STARTVALUE = 0  # mA
MAGNET_STEPSIZE = 100  # mA
MAGNET_ENDVALUE = 3000  # mA
VELOCITY_STARTVALUE = 0  # mA
VELOCITY_STEPSIZE = 10  # mA
VELOCITY_ENDVALUE = 300  # mA

# Magnet output
port_magnet = PortSelector.get_port_of('rs')
assert port_magnet
magnet_output_device = RS3000Output(
    port=port_magnet,
    voltage_limit=30,
    current_limit=3000,
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
port_rbd = PORT_RBD
assert port_rbd
input_device = RBDInput(
    port=port_rbd,
    rbd_sample_rate=CURRENT_SAMPLERATE,
    pull_rate=CURRENT_PULLRATE,
    unit=RBDInput.CurrentUnit.NANO
)

# Setup GUI
with input_device, magnet_output_device, velocity_output_device:
    input_device.start_sampling(CURRENTGRAPH_REFRESHRATE)
    win = MainWindow(high_resolution=False)
    magnet_component = Output(
        max_value=MAGNETCONTROL_MAXCURRENT,
        interface=magnet_output_device,
        parent=win.main_widget(),
        name="Magnet",
        unit="mA"
    )
    velocity_filter_component = Output(
        max_value=VELOCITYCONTROL_MAXVOLTAGE,
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
    gs = GridSearch(input=input_device,
                    measuring_time=MEASURING_TIME,
                    parent=win.main_widget(),
                    move_knobs=True,
                    measurement_str='Battery Current')
    volt_values = [round(x) for x in np.arange(VELOCITY_STARTVALUE, VELOCITY_ENDVALUE+VELOCITY_STEPSIZE/2, VELOCITY_STEPSIZE)]
    magnet_values = [round(x) for x in np.arange(MAGNET_STARTVALUE, MAGNET_ENDVALUE+MAGNET_STEPSIZE/2, MAGNET_STEPSIZE)]
    gs.add_device(magnet_component, magnet_values, 1)
    gs.add_device(velocity_filter_component, volt_values, 1)
    plot = PlotStream(parent=win.main_widget(), input=input_device, timespan=30)
    win.add_children(magnet_component, velocity_filter_component, input_component, gs, plot)
    win.run()
