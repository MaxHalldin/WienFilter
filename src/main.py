import numpy as np
# Hardware interface classes
from pythion.connections import RS3000Output, PicoOutput, PortSelector, LinearCalibration, MockOutput, InterpolCalibration, OutputInterface, MockInput

# GUI Classes
from pythion import Output, Input, MainWindow, PlotStream, Action

from grid_search import grid_search

op1 = MockOutput()
op2 = MockOutput()

# Setup GUI
inp = MockInput()

with op1, op2, inp:
    inp.start_sampling(10)
    win = MainWindow(high_resolution=False)
    com1 = Output(max_value=400, interface=op1, parent=win.main_widget(), name="High voltage supply", unit="V")
    com2 = Output(max_value=400, interface=op2, parent=win.main_widget(), name="High voltage supply", unit="V")

    value_list = [round(x) for x in np.linspace(0, 100, 11)]
    grid_search_args = [
        (com1, value_list, 0.1),
        (com2, value_list, 0.1)
    ]
    grid_search_kwargs = {
        'measure': (lambda: 5)
    }
    action = Action(grid_search, grid_search_args, grid_search_kwargs, parent=win.main_widget(), text='Tryck på mig!')
    # input_component = Input(interface=inp, name='Beam current', unit='nA', parent=win.main_widget())
    plt = PlotStream(parent=win.main_widget(), input=inp, timespan=10, fix_scale=False)
    win.add_children(com1, com2, action, plt)
    win.run()
