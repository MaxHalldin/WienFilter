from pythion.gui import MainWindow, Output, PlotStream, Input, Action
from pythion.connections import MockOutput, MockBufferInput, LinearCalibration
from pythion.routines import GridSearch
from pythion._routines.time_series import TimeSeries
from pythion._routines.file_handling import FileSettings

cal = LinearCalibration(35)
op1 = MockOutput(control_limit=10, calibration=cal)
op2 = MockOutput()
op1.add_invalid_output_handler(print)

# Setup GUI
inp = MockBufferInput(buffer=False, pull_on_buffer_read=True, rate=50)

win = MainWindow(high_resolution=False)
velocity_filter = Output(max_value=300,
                         interface=op1,
                         parent=win.main_widget(),
                         name="Velocity filter",
                         unit="V")
magnet = Output(max_value=1000, interface=op2, parent=win.main_widget(), name="Magnet", unit="mA")
input_component = Input(interface=inp, rate=5, name='Beam current', unit='nA', parent=win.main_widget())

grid_search = GridSearch(
    GridSearch.Device.from_stepsize(magnet, 0.5, 3000, 0, -1000),
    GridSearch.Device.from_stepsize(velocity_filter, 0.5, 0, 300, 10),
    input=input_component,
    settings=GridSearch.GridSearchSettings(11, 0.2, True, plot_every=10),
    plot_settings=GridSearch.HeatmapSettings(0, 3000, 10),
    file_settings=FileSettings('results', './gridresults')
)
time_series = TimeSeries([velocity_filter, magnet], input_component)

start_button = Action(routine=grid_search, parent=win.main_widget(), text='Grid Search')
start_button2 = Action(routine=time_series, parent=win.main_widget(), text='Time series')

plt = PlotStream(parent=win.main_widget(), input=inp, timespan=30, fix_scale=False)
win.add_children(velocity_filter, magnet, plt, input_component, start_button, start_button2)

with magnet, velocity_filter, input_component:
    win.run()
