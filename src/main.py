import numpy as np
# Hardware interface classes
from pythion.connections import MockOutput, MockBufferInput
# GUI Classes
from pythion import MainWindow, Output, PlotStream

from pythion.grid_search import GridSearch

op1 = MockOutput()
op2 = MockOutput()

# Setup GUI
inp = MockBufferInput(buffer=False, pull_on_buffer_read=True, rate=10)

with op1, op2, inp:
    inp.start_sampling(10)
    win = MainWindow(high_resolution=False)
    com1 = Output(max_value=300, interface=op1, parent=win.main_widget(), name="Velocity filter", unit="V")
    com2 = Output(max_value=1000, interface=op2, parent=win.main_widget(), name="Magnet", unit="mA")
    gs = GridSearch(input=inp, measuring_time=0.1, parent=win.main_widget(), move_knobs=True, plot_every=3, measurement_str=None)
    volt_values = [round(x) for x in np.arange(0, 301, 30)]
    mamp_values = [round(x) for x in np.arange(0, 1001, 100)]
    gs.add_device(com1, volt_values, 0.)
    gs.add_device(com2, mamp_values, 0.)

    # input_component = Input(interface=inp, name='Beam current', unit='nA', parent=win.main_widget())
    plt = PlotStream(parent=win.main_widget(), input=inp, timespan=30, fix_scale=False)
    win.add_children(com1, com2, gs, plt)
    win.run()
