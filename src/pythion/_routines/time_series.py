from time import sleep
import matplotlib.pyplot as plt
from pythion._routines.measurement_routine import MeasurementRoutine
from pythion._connections.buffer_input import BufferInput
from pythion._routines.file_handling import FileSettings, generate_filename

VALUES = [
    (0, 0),
    (0, 150)
]
WAIT_TIME = 2


class TimeSeries(MeasurementRoutine):
    def __init__(self, devices, input):
        super().__init__()
        self.add_task(self.execute)
        self.devices = devices
        self.buffer_input = input.interface

    def execute(self):
        assert isinstance(self.buffer_input, BufferInput)
        measurements = []
        start_indices = []
        for value in VALUES:
            start_indices.append(len(measurements))
            self._set_value(value)
            self.buffer_input.restart_buffer()
            sleep(WAIT_TIME)
            measurements.extend(self.buffer_input.get_buffer())
        self.run_on_main_thread(self._plot_res, measurements, start_indices)

        with open(generate_filename(FileSettings('timeseries', path='./timeseries', extension='txt')), 'x') as file:
            file.write(str(measurements) + '\n')
            file.write(str(start_indices))
        print(measurements)
        print(start_indices)

    @staticmethod
    def _plot_res(measurements, start_indices):
        ymin = min(measurements)
        ymax = max(measurements)
        _, ax = plt.subplots()
        ax.plot(list(range(len(measurements))), measurements, 'x-')
        ax.vlines(start_indices, ymin, ymax, colors=['k'], linestyles='dashed')
        plt.show(block=False)

    def _set_value(self, values):
        for val, dev in zip(values, self.devices):
            self.set_output(dev, val, block=False)
