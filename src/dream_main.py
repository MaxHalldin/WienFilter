from pythion.gui import MainWindow, Output, PlotStream, Input
from pythion.connections import MockOutput, MockBufferInput, LinearCalibration

from grid_search import grid_seach_function

win = MainWindow(high_resolution=False)

output1 = Output.factory(
    type=Output.Type.RS3005P,
    name='Velocity filter',
    unit='V',
    control_maximum=10,
    target_maximum=300,
    knob_limit=300,
    calibration=LinearCalibration(35),
    parent=win
)

output1 = Output.factory(
    type=Output.Type.RS3005P,
    name='Magnet',
    unit='mA',
    target_maximum=2000,
    knob_limit=2000,
    parent=win
)

# Setup GUI
inp1 = Input.factory(
    type=Input.Type.RBDPICOAMMETER,
    name='Beam Current',
    unit='nA',
    buffer=False,
    pull_on_buffer_read=True,
    rate=1,
    parent=win
)


plt = inp1.get_plot(
    timespan=30,
    fix_scale=False
)

gridsearch = GridSearch(
    GridSeachDevice.from_start_stop_step(
        output=output1,
        start=0,
        step=10,
        stop=100,
        wait_time=0.2
    ),
    GridSeachDevice.from_start_stop_step(
        output=output2,
        start=0,
        step=10,
        stop=100,
        wait_time=0.2
    ),
    measuring_time=0.01,
    plot_every=100,
    update_settings=ValueUpdateSettings.NO_UPDATE
)

action = Action(
    routine=gridsearch,
    params=[
        Action.Param('Velocity Start Value:', int, 0, 100),
        Action.Param('Veloctiy Step Size', int, 0, 100),
        Action.Param('Velocity End Value', int, 0, 100),
        Action.Param('Velocity Start Value:', int, 0, 100),
        Action.Param('Veloctiy Step Size', int, 0, 100),
        Action.Param('Velocity End Value', int, 0, 100)
    ]
)

win.run()

