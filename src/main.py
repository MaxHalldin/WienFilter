import numpy as np
# Hardware interface classes
from pythion.connections import RS3000Output, PicoOutput, PortSelector, LinearCalibration, MockOutput, InterpolCalibration, OutputInterface, MockInput

# GUI Classes
from pythion import Output, Input, MainWindow, PlotStream, Action, HeatMap

from grid_search import grid_search
import random

op1 = MockOutput()
op2 = MockOutput()

# Setup GUI
inp = MockInput()

with op1, op2, inp:
    inp.start_sampling(10)
    win = MainWindow(high_resolution=False)
    com1 = Output(max_value=300, interface=op1, parent=win.main_widget(), name="Velocity filter", unit="V")
    com2 = Output(max_value=1000, interface=op2, parent=win.main_widget(), name="Magnet", unit="mA")
    heatmap = HeatMap(parent=win.main_widget())

    volt_values = [round(x) for x in np.arange(0, 300, 50)]
    mamp_values = [round(x) for x in np.arange(0, 1000, 100)]
    grid_search_args = [
        (com1, volt_values, 0.1),
        (com2, mamp_values, 0.1)
    ]
    grid_search_kwargs = {
        'measure': (lambda: random.random()),
        'result_plot': heatmap
    }
    action = Action(grid_search, grid_search_args, grid_search_kwargs, parent=win.main_widget(), text='Tryck på mig!')
    # input_component = Input(interface=inp, name='Beam current', unit='nA', parent=win.main_widget())
    plt = PlotStream(parent=win.main_widget(), input=inp, timespan=10, fix_scale=False)
    win.add_children(com1, com2, action, heatmap, plt)
    win.run()
