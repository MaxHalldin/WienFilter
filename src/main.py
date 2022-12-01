import numpy as np

from pythion.gui import MainWindow, Output, PlotStream, GridSearch, Input
from pythion.connections import MockOutput, MockBufferInput, LinearCalibration

cal = LinearCalibration(35)
op1 = MockOutput(control_limit=10, calibration=cal)
op2 = MockOutput()
op1.add_invalid_output_handler(print)

# Setup GUI
inp = MockBufferInput(buffer=False, pull_on_buffer_read=True, rate=10)

win = MainWindow(high_resolution=False)
com1 = Output(max_value=300,
              interface=op1,
              parent=win.main_widget(),
              name="Velocity filter",
              unit="V")
com2 = Output(max_value=1000, interface=op2, parent=win.main_widget(), name="Magnet", unit="mA")
gs = GridSearch(input=inp, measuring_time=0.1, parent=win.main_widget(), move_knobs=False, plot_every=1, measurement_str=None)
volt_values = [round(x) for x in np.arange(0, 501, 100)]
mamp_values = [round(x) for x in np.arange(0, 1001, 100)]
gs.add_device(com1, volt_values, 0.5)
gs.add_device(com2, mamp_values, 0.5)

input_component = Input(interface=inp, rate=5, name='Beam current', unit='nA', parent=win.main_widget())
plt = PlotStream(parent=win.main_widget(), input=inp, timespan=30, fix_scale=False)
win.add_children(com1, com2, gs, plt, input_component)

with com1, com2, input_component:
    win.run()
