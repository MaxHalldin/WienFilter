from pythion.gui import MainWindow, Output, PlotStream, Input, Action
from pythion.connections import RS3000Output, RBDInput, LinearCalibration, PowerOptions
from pythion.routines import GridSearch
from pythion._routines.time_series import TimeSeries
from pythion._routines.file_handling import FileSettings

PORT_RBD = 'COM0'
PORT_VELOCITY = 'COM0'
PORT_MAGNET = 'COM0'

# Lab GUI parameters, to be read from config file!
#   Device setting params
MAGNET_MAXCURRENT = 3000  # mA
VELOCITY_MAXVOLTAGE = 300  # V
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

cal = LinearCalibration(35)
velocity_filter = RS3000Output(
    port=PORT_VELOCITY,
    control_limit=10,
    target_limit=VELOCITY_MAXVOLTAGE,
    calibration=cal,
    mode=PowerOptions.VOLTAGE
)

magnet = RS3000Output(
    port=PORT_MAGNET,
    target_limit=MAGNET_MAXCURRENT,
    mode=PowerOptions.CURRENT
)

# Setup GUI
# Input
port_rbd = PORT_RBD
assert port_rbd
input_device = RBDInput(
    port=PORT_RBD,
    rbd_sample_rate=CURRENT_SAMPLERATE,
    pull_rate=CURRENT_PULLRATE,
    unit=RBDInput.CurrentUnit.NANO,
    discard_unstable=False
)

win = MainWindow(high_resolution=False)
velocity_filter = Output(max_value=VELOCITY_MAXVOLTAGE,
                         interface=velocity_filter,
                         parent=win.main_widget(),
                         name="Velocity filter",
                         unit="V")

magnet = Output(max_value=MAGNET_MAXCURRENT, interface=magnet, parent=win.main_widget(), name="Magnet", unit="mA")
input_component = Input(interface=input_device, rate=CURRENTGRAPH_REFRESHRATE, name='Beam current', unit='nA', parent=win.main_widget())

grid_search = GridSearch(
    GridSearch.Device.from_stepsize(magnet, MAGNET_SETTIME, MAGNET_ENDVALUE, MAGNET_STARTVALUE, -MAGNET_STEPSIZE),
    GridSearch.Device.from_stepsize(velocity_filter, VELOCITY_SETTIME, VELOCITY_STARTVALUE, VELOCITY_ENDVALUE, VELOCITY_STEPSIZE),
    input=input_component,
    settings=GridSearch.GridSearchSettings(MEASURING_TIME, True, plot_every=1),
    plot_settings=GridSearch.HeatmapSettings(0, 3000, 10),
    file_settings=FileSettings('results', './gridsearch')
)

time_series = TimeSeries([velocity_filter, magnet], input_component)
start_button = Action(routine=grid_search, parent=win.main_widget(), text='Grid Search')
start_button2 = Action(routine=time_series, parent=win.main_widget(), text='Time series')

plt = PlotStream(parent=win.main_widget(), input=input_component, timespan=60, fix_scale=False)
win.add_children(velocity_filter, magnet, plt, input_component, start_button, start_button2)

with magnet, velocity_filter, input_component:
    win.run()
