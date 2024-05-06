import sys
import traceback
import logging

logger = logging.getLogger('pythion')

DEMO = True


def log_error(description: str, tb: str):
    tb = tb.split('\n')
    tb = [(40 * ' ') + line.lstrip() for line in tb]
    tb = '\n'.join(tb)
    logger.error(f'                {description} {tb.lstrip()}')


try:
    # Imports from the pythion package are wrapped in the try block too,
    # so that any import-time errors are caught and logged properly.
    from src.pythion.gui import MainWindow, Output, PlotStream, Input, Action
    from src.pythion.connections import LinearCalibration, RS3000Output, PowerOptions, RBDInput, MockBufferInput, MockOutput
    from src.pythion.routines import GridSearch, Heatmap
    from src.pythion._routines.file_handling import FileSettings

    params = {}
    with open('config.txt', 'r') as file:
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
        "PORT_RBD2",
        "PORT_RBD3",
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
        "MEASURING_SAMPLES",
        "MAGNET_STARTVALUE",
        "MAGNET_STEPSIZE",
        "MAGNET_ENDVALUE",
        "VELOCITY_STARTVALUE",
        "VELOCITY_STEPSIZE",
        "VELOCITY_ENDVALUE",
        "PLOT_EVERY",
        "RESET_AFTER_GRIDSEARCH",
        "HEATMAP_SCALEMIN",
        "HEATMAP_SCALEMAX",
        "HEATMAP_LOGLIMIT",
        "RESULTS_FILENAME",
        "RESULTS_FOLDERNAME",
        "RESULTS_TIMESTAMP",
        "STREAMPLOT_TIMESPAN",
        "STREAMPLOT_FIXSCALE",
        "HEATMAP_MAXLABELS",
        "VELOCITY_BIDIRECTIONAL"
    ]
    for key in param_keys:
        if key not in params:
            raise Exception(f'key parameter "{key}" not in config file!')

    cal = LinearCalibration(35)
    if DEMO:
        velocity_filter = MockOutput(
            control_limit=10,
            target_limit=params['VELOCITY_MAXVOLTAGE'],
            calibration=cal,
        )
        magnet = MockOutput(target_limit=params['MAGNET_MAXCURRENT'])
        input_device = MockBufferInput(pull_rate=params['CURRENT_PULLRATE'])
        input_device_2 = MockBufferInput(pull_rate=params['CURRENT_PULLRATE'])
        input_device_3 = MockBufferInput(pull_rate=params['CURRENT_PULLRATE'])
    else:
        velocity_filter = RS3000Output(
            port=params['PORT_VELOCITY'],
            control_limit=10,
            target_limit=params['VELOCITY_MAXVOLTAGE'],
            calibration=cal,
            mode=PowerOptions.VOLTAGE
        )
        magnet = RS3000Output(
            port=params['PORT_MAGNET'],
            target_limit=params['MAGNET_MAXCURRENT'],
            mode=PowerOptions.CURRENT
        )
        input_device = RBDInput(
            port=params['PORT_RBD'],
            rbd_sample_rate=params['CURRENT_SAMPLERATE'],
            pull_rate=params['CURRENT_PULLRATE'],
            unit=RBDInput.CurrentUnit.NANO,
            discard_unstable=True
        )
        input_device_2 = RBDInput(
            port=params['PORT_RBD2'],
            rbd_sample_rate=params['CURRENT_SAMPLERATE'],
            pull_rate=params['CURRENT_PULLRATE'],
            unit=RBDInput.CurrentUnit.NANO,
            discard_unstable=True
        )
        input_device_3 = RBDInput(
            port=params['PORT_RBD3'],
            rbd_sample_rate=params['CURRENT_SAMPLERATE'],
            pull_rate=params['CURRENT_PULLRATE'],
            unit=RBDInput.CurrentUnit.NANO,
            discard_unstable=True
        )

    win = MainWindow(high_resolution=False, master_error_handler=log_error)
    velocity_filter = Output(
        max_value=params['VELOCITY_MAXVOLTAGE'],
        interface=velocity_filter,
        name="Velocity filter",
        unit="V"
    )

    magnet = Output(max_value=params['MAGNET_MAXCURRENT'], interface=magnet, name="Magnet", unit="mA")
    input_component = Input(interface=input_device, rate=params['STREAMPLOT_REFRESHRATE'], name='Beam current', unit='nA')
    input_component_2 = Input(interface=input_device_2, rate=params['STREAMPLOT_REFRESHRATE'], name='Beam current 2', unit='nA')
    input_component_3 = Input(interface=input_device_3, rate=params['STREAMPLOT_REFRESHRATE'], name='Beam current 3', unit='nA')

    gridsearch_settings = GridSearch.Settings(measure_samples=params['MEASURING_SAMPLES'],
                                              measure_checktime=1/params['CURRENT_PULLRATE'],
                                              update_graphics=True,
                                              plot_every=params['PLOT_EVERY'],
                                              reset_to_zero=params['RESET_AFTER_GRIDSEARCH'])
    grid_search = GridSearch(
        GridSearch.Device.from_stepsize(magnet, params['MAGNET_SETTIME'], params['MAGNET_STARTVALUE'], params['MAGNET_ENDVALUE'], params['MAGNET_STEPSIZE']),
        GridSearch.Device.from_stepsize(velocity_filter, params['VELOCITY_SETTIME'], params['VELOCITY_STARTVALUE'], params['VELOCITY_ENDVALUE'],
                                        params['VELOCITY_STEPSIZE'], bidirectional=params['VELOCITY_BIDIRECTIONAL']),
        input=input_component,
        settings=gridsearch_settings,
        plot_settings=Heatmap.Settings(params['HEATMAP_SCALEMIN'], params['HEATMAP_SCALEMAX'], params['HEATMAP_LOGLIMIT'], params['HEATMAP_MAXLABELS']),
        file_settings=FileSettings(params['RESULTS_FILENAME'], './' + params['RESULTS_FOLDERNAME'], timestamp=params['RESULTS_TIMESTAMP'])
    )

    start_button = Action(routine=grid_search, text='Grid Search')

    plt = PlotStream(input=input_device, timespan=params['STREAMPLOT_TIMESPAN'], fix_scale=params['STREAMPLOT_FIXSCALE'])
    win.add_children(velocity_filter, magnet, start_button, plt.frame) ### IT IS HERE WE CAN CHANGHE THE ORDER OF PANELS

    win.add_vert(2)
    win.add_vert_children(input_component, input_component_2, input_component_3)
        
except Exception:
    # Hanldes exceptions that occur before starting the GUI
    log_error('An error occured while setting up the program.', traceback.format_exc())
    # Indent the error for logging
    print('An error occured before the program could be started. Traceback has been written to the log.')
    sys.exit(1)

with magnet, velocity_filter, input_component:
    exit_code = win.run()

sys.exit(exit_code)
