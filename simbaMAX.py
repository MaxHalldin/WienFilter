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
    from srcMAX.pythionMAX.guiMAX import MainWindow, Output, PlotStream, Input, Action, CAEN
    from srcMAX.pythionMAX.connectionsMAX import LinearCalibration, RS3000Output, PowerOptions, RBDInput, MockBufferInput, MockOutput, MockCAEN
    from srcMAX.pythionMAX.routinesMAX import GridSearch, Heatmap
    from srcMAX.pythionMAX._routinesMAX.file_handlingMAX import FileSettings
    from srcMAX.pythionMAX.connectionsMAX import CAENOutput

    params = {}
    with open('configMAX.txt', 'r') as file: #location might need to be adjusted 
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
        "PORT_CAEN",
        "PORT_RBD_a",
        "PORT_RBD_s",
        "PORT_RBD_fc",
        "PORT_VELOCITY",
        "PORT_MAGNET",
        "MAGNET_MAXCURRENT",
        "VELOCITY_MAXVOLTAGE",
        "CURRENT_SAMPLERATE",
        "CURRENT_PULLRATE",
        "STREAMPLOT_REFRESHRATE",
        "DISCARD_UNSTABLE",
        "CAEN_UPDATE_RATE",
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
        input_device_a = MockBufferInput(pull_rate=params['CURRENT_PULLRATE'])
        input_device_s = MockBufferInput(pull_rate=params['CURRENT_PULLRATE'])
        input_device_fc = MockBufferInput(pull_rate=params['CURRENT_PULLRATE'])
        CAEN_device = MockCAEN()

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
        input_device_a = RBDInput(
            port=params['PORT_RBD_a'],
            rbd_sample_rate=params['CURRENT_SAMPLERATE'],
            pull_rate=params['CURRENT_PULLRATE'],
            unit=RBDInput.CurrentUnit.NANO,
            discard_unstable=True
        )
        input_device_s = RBDInput(
            port=params['PORT_RBD_s'],
            rbd_sample_rate=params['CURRENT_SAMPLERATE'],
            pull_rate=params['CURRENT_PULLRATE'],
            unit=RBDInput.CurrentUnit.NANO,
            discard_unstable=True
        )
        input_device_fc = RBDInput(
            port=params['PORT_RBD_fc'],
            rbd_sample_rate=params['CURRENT_SAMPLERATE'],
            pull_rate=params['CURRENT_PULLRATE'],
            unit=RBDInput.CurrentUnit.NANO,
            discard_unstable=True
        )
        CAEN_device = CAENOutput(port=params['PORT_CAEN'],
                                 bd='0',
                                 pullRate=params['CAEN_UPDATE_RATE'],
                                 )

    win = MainWindow(high_resolution=False, master_error_handler=log_error)
    velocity_filter = Output(
        max_value=params['VELOCITY_MAXVOLTAGE'],
        interface=velocity_filter,
        name="Velocity filter",
        unit="V"
    )

    magnet = Output(max_value=params['MAGNET_MAXCURRENT'], interface=magnet, name="Magnet", unit="mA")
    input_component_a = Input(interface=input_device_a, rate=params['STREAMPLOT_REFRESHRATE'], name='Aperature current', unit='nA')
    input_component_s = Input(interface=input_device_s, rate=params['STREAMPLOT_REFRESHRATE'], name='Sample current', unit='nA')
    input_component_fc = Input(interface=input_device_fc, rate=params['STREAMPLOT_REFRESHRATE'], name='FC current', unit='nA')

    CAEN_device = CAEN(interface=CAEN_device, unit='0', rate=5)

    gridsearch_settings = GridSearch.Settings(measure_samples=params['MEASURING_SAMPLES'],
                                              measure_checktime=1/params['CURRENT_PULLRATE'],
                                              update_graphics=True,
                                              plot_every=params['PLOT_EVERY'],
                                              reset_to_zero=params['RESET_AFTER_GRIDSEARCH'])
    grid_search = GridSearch(
        GridSearch.Device.from_stepsize(magnet, params['MAGNET_SETTIME'], params['MAGNET_STARTVALUE'], params['MAGNET_ENDVALUE'], params['MAGNET_STEPSIZE']),
        GridSearch.Device.from_stepsize(velocity_filter, params['VELOCITY_SETTIME'], params['VELOCITY_STARTVALUE'], params['VELOCITY_ENDVALUE'],
                                        params['VELOCITY_STEPSIZE'], bidirectional=params['VELOCITY_BIDIRECTIONAL']),
        input=input_component_s,
        settings=gridsearch_settings,
        plot_settings=Heatmap.Settings(params['HEATMAP_SCALEMIN'], params['HEATMAP_SCALEMAX'], params['HEATMAP_LOGLIMIT'], params['HEATMAP_MAXLABELS']),
        file_settings=FileSettings(params['RESULTS_FILENAME'], './' + params['RESULTS_FOLDERNAME'], timestamp=params['RESULTS_TIMESTAMP'])
    )

    start_button = Action(routine=grid_search, text='Grid Search')

    plt = PlotStream(input=input_device_s, timespan=params['STREAMPLOT_TIMESPAN'], fix_scale=params['STREAMPLOT_FIXSCALE'])
    win.add_children(velocity_filter, magnet, start_button, plt.frame)
    win.add_vert(2)     #'2' refers to the position counting from left.
    win.add_vert_children(input_component_a, input_component_fc, input_component_s)
    win.add_CAEN(CAEN_device)

except Exception:
    # Hanldes exceptions that occur before starting the GUI
    log_error('An error occured while setting up the program.', traceback.format_exc())
    # Indent the error for logging
    print('An error occured before the program could be started. Traceback has been written to the log.')
    sys.exit(1)

with magnet, velocity_filter, input_component_a, input_component_fc, input_component_s, CAEN_device:
    exit_code = win.run()

sys.exit(exit_code)
