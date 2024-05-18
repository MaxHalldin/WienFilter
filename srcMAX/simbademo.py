from pythion.gui import MainWindow, Output, PlotStream, Input, Action
from pythion.connections import LinearCalibration, MockOutput, MockBufferInput
from pythion.routines import GridSearch, Heatmap
from pythion._routines.file_handling import FileSettings

import logging
logger = logging.Logger('pythion')

params = {}

with open('src/config.txt', 'r') as file:
    for line in file.readlines():
        try:
            code, *_ = line.split('#', 1)  # Get rid of comments in config file
            if not code.strip():
                continue
            key, value_string = code.strip().split(': ')
            params[key] = eval(value_string)
        except Exception:
            logger.warning(f'Cannot interpret line "{line}"')
            continue

param_keys = [
    "PORT_RBD",
    "PORT_VELOCITY",
    "PORT_MAGNET",
    "MAGNET_MAXCURRENT",
    "VELOCITY_MAXVOLTAGE",
    "CURRENT_SAMPLERATE",
    "CURRENT_PULLRATE",
    "STREAMPLOT_REFRESHRATE",
    "DISCARD_UNSTABLE",
    "MAGNET_SETTIME",
    "VELOCITY_SETTIME",
    "MEASURING_CHECKTIME",
    "MEASURING_SAMPLES",
    "MAGNET_STARTVALUE",
    "MAGNET_STEPSIZE",
    "MAGNET_ENDVALUE",
    "VELOCITY_STARTVALUE",
    "VELOCITY_STEPSIZE",
    "VELOCITY_ENDVALUE",
    "PLOT_EVERY",
    "HEATMAP_SCALEMIN",
    "HEATMAP_SCALEMAX",
    "HEATMAP_LOGLIMIT",
    "RESULTS_FILENAME",
    "RESULTS_FOLDERNAME",
    "RESULTS_TIMESTAMP",
    "STREAMPLOT_TIMESPAN",
    "STREAMPLOT_FIXSCALE"
]
for key in param_keys:
    if key not in params:
        raise Exception(f'Key parameter "{key}" not in config file!')

cal = LinearCalibration(35)
velocity_filter = MockOutput(
    control_limit=10,
    target_limit=params['VELOCITY_MAXVOLTAGE'],
    calibration=cal,
)

magnet = MockOutput(
    target_limit=params['MAGNET_MAXCURRENT'],
)

input_device = MockBufferInput(
    pull_rate=params['CURRENT_PULLRATE']
)

win = MainWindow(high_resolution=False)
velocity_filter = Output(max_value=params['VELOCITY_MAXVOLTAGE'],
                         interface=velocity_filter,
                         parent=win.main_widget(),
                         name="Velocity filter",
                         unit="V")

magnet = Output(max_value=params['MAGNET_MAXCURRENT'], interface=magnet, parent=win.main_widget(), name="Magnet", unit="mA")
input_component = Input(interface=input_device, rate=params['STREAMPLOT_REFRESHRATE'], name='Beam current', unit='nA', parent=win.main_widget())

grid_search = GridSearch(
    GridSearch.Device.from_stepsize(magnet, params['MAGNET_SETTIME'], params['MAGNET_STARTVALUE'], params['MAGNET_ENDVALUE'], params['MAGNET_STEPSIZE']),
    GridSearch.Device.from_stepsize(velocity_filter, params['VELOCITY_SETTIME'], params['VELOCITY_STARTVALUE'], params['VELOCITY_ENDVALUE'],
                                    params['VELOCITY_STEPSIZE']),
    input=input_component,
    settings=GridSearch.Settings(params['MEASURING_SAMPLES'], params['MEASURING_CHECKTIME'], True, plot_every=params['PLOT_EVERY']),
    plot_settings=Heatmap.Settings(params['HEATMAP_SCALEMIN'], params['HEATMAP_SCALEMAX'], params['HEATMAP_LOGLIMIT']),
    file_settings=FileSettings(params['RESULTS_FILENAME'], './' + params['RESULTS_FOLDERNAME'], timestamp=params['RESULTS_TIMESTAMP'])
)

start_button = Action(routine=grid_search, parent=win.main_widget(), text='Grid Search')

plt = PlotStream(parent=win.main_widget(), input=input_device, timespan=params['STREAMPLOT_TIMESPAN'], fix_scale=params['STREAMPLOT_FIXSCALE'])
win.add_children(velocity_filter, magnet, plt, input_component, start_button)

with magnet, velocity_filter, input_component:
    win.run()
