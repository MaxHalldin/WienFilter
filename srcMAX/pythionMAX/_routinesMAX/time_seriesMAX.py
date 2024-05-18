from time import sleep
import matplotlib.pyplot as plt
import logging

from srcMAX.pythionMAX._connectionsMAX.rbd_inputMAX import RBDInput
from srcMAX.pythionMAX._routinesMAX.measurement_routineMAX import MeasurementRoutine
from srcMAX.pythionMAX._connectionsMAX.buffer_inputMAX import BufferInput
from srcMAX.pythionMAX._routinesMAX.file_handlingMAX import FileSettings, generate_filename

logger = logging.getLogger('pythion')

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
        self.input = input
        self.buffer_input = input.interface

    def execute(self):
        assert isinstance(self.buffer_input, BufferInput)
        measurements = []
        start_indices = []
        logger.debug('TimeSeries:     starting time series measurement')
        for value in VALUES:
            start_indices.append(len(measurements))
            self._set_value(value)
            self.buffer_input.restart_buffer()
            sleep(WAIT_TIME)
            measurements.extend(self.buffer_input.get_buffer())
        self.run_on_main_thread(self._plot_res, measurements, start_indices)

        logger.debug('TimeSeries:     finished time series measurement')

        with open(generate_filename(FileSettings('timeseries', path='./timeseries', extension='txt')), 'x') as file:
            file.write('Settings:\n')
            file.write('    Devices:\n')
            for device in self.devices:
                file.write(f'       {device}\n')
            file.write('    Values\n')
            for val in VALUES:
                file.write(f'       {val}\n')
            file.write('    Output:\n')
            file.write(f'        {self.input}\n')
            if isinstance(self.buffer_input, RBDInput):
                file.write('Sample rate:\n')
                file.write(f'   {self.buffer_input.rbd_sample_rate}')
            file.write('\nMeasurements:\n')
            file.write(str(measurements) + '\n')
            file.write('\nNew output setting indices:\n')
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
