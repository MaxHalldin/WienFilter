# Hardware interface classes
from pythion.connections import PortSelector, RBDInput

# GUI Classes
from pythion import Output, Input, MainWindow, PlotStream

# Input
port_rbd = PortSelector.get_port_of('rbd')
inp = RBDInput(
    port=port_rbd,
    rbd_sample_rate=5,
    pull_rate=5,
    unit=RBDInput.CurrentUnit.NANO
)

# Setup GUI

with inp:
    inp.start_sampling(5)
    win = MainWindow(high_resolution=False)

    input_component = Input(interface=inp, name='Beam current', unit='nA', parent=win.main_widget())
    plt_component = PlotStream(parent=win.main_widget(), input=inp, timespan=10, fix_scale=False)
    win.add_children(input_component, plt_component)
    win.run()
