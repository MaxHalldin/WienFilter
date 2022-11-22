# Hardware interface classes
from pythion.connections import RS3000Output, PicoOutput, PortSelector, LinearCalibration, MockOutput, InterpolCalibration, OutputInterface, MockInput

# GUI Classes
from pythion import Output, Input, MainWindow, PlotStream
from pythion._connections.buffer_input import PicoMockBufferInput

from threading import Timer
PICO = False
RS = False


# Define invalid input handler
def on_invalid() -> None:
    print('Invalid!')


# Define hardware intefaces:
# RS 3005P
MAX_VOLTAGE_RS = 5
MAX_CURRENT_RS = 50
MODE_RS = RS3000Output.PowerOptions.CURRENT
INPUT_MAX_RS = MAX_VOLTAGE_RS if MODE_RS == RS3000Output.PowerOptions.VOLTAGE else MAX_CURRENT_RS
CALIBRATION_RS = InterpolCalibration.from_file("testcal.csv", True)

rs: OutputInterface
pico: OutputInterface
if RS:
    port_rs = PortSelector.get_port_of('rs')
    assert port_rs is not None
    rs = RS3000Output(port=port_rs,
                      calibration=CALIBRATION_RS,
                      voltage_limit=MAX_VOLTAGE_RS,
                      current_limit=MAX_CURRENT_RS,
                      mode=MODE_RS)
else:
    rs = MockOutput()

# Pico
MAX_VOLTAGE_PICO = 350
CALIBRATION_PICO = LinearCalibration(350)
if PICO:
    port_pico = PortSelector.get_port_of('pico')
    assert port_pico is not None
    pico = PicoOutput(port=port_pico, calibration=CALIBRATION_PICO, voltage_limit=MAX_VOLTAGE_PICO)
else:
    pico = MockOutput()

# Input
port_pico = PortSelector.get_port_of('pico')
inp = MockInput()

# Setup GUI

with rs, pico, inp:
    inp.start_sampling(10)
    win = MainWindow(high_resolution=False)
    pico_component = Output(max_value=400, interface=pico, parent=win.main_widget(), name="High voltage supply", unit="V")
    # rs_component = Output(max_value=INPUT_MAX_RS, interface=rs, parent=win, name="Magnet current", unit="mA")

    def reset() -> None:
        pico_component.set_value(0, True)
    t = Timer(10, reset)
    input_component = Input(interface=inp, name='Beam current', unit='nA', parent=win.main_widget())
    plt = PlotStream(parent=win.main_widget(), input=inp, timespan=10, fix_scale=False)
    plt.set_ylim((0, 100))
    win.add_children(pico_component, input_component, plt)
    t.start()
    win.run()
