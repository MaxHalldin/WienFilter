from interfaces.usb import USB
from interfaces.calibration import Calibration, LinearCalibration
from interfaces.output import Output

class PicoOutput(Output):
    """
    Specialization of the Output class for a Pico running a DAC for a voltage supply.
    Target signal is the output voltage of the voltage supply.
    Control signal is a 0-1 float corresponding to minimum/maximum output of the DAC.

    Setting voltage_limit allows for a safety-check if a higher voltage is set.
    Setting a value that's out of bounds for the DAC will result in a maximum/minimum
    signal being sent (provided that the target voltage is safe)
    """
    def __init__(self, port: str, calibration: Calibration, voltage_limit: float = None, bits = 12):
        self._usb = USB(port)
        self.voltage_limit = voltage_limit
        self.bits = bits
        self._last_control = None # Use this local variable to overwrite control signal getter,
                                  # as this might differ if value is out of DAC range.
        super().__init__(0, calibration)
    
    def __enter__(self):
        self._usb.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_value, tb):
        self._usb.__exit__(exc_type, exc_value, tb)
    
    @Output.target.setter
    def target(self, value: float):
        if self.voltage_limit is not None and value > self.voltage_limit:
            raise ValueError(f'A voltage of {value} exceeds the listed DAC capability.')
        Output.target.fset(self, value)
    
    @Output.control.getter
    def control(self):
        return self._last_control

    def _write(self, control: float) -> None:
        """
        Write signal to DAC. control is a float between 0 and 1,
        and will be converted to a binary number.
        """
        control = max(min(control, 1), 0) # Make sure control signal is within range
        self._last_control = control
        binary = round(control * (2**self.bits - 1)) # Discretize
        self._usb.write(str(binary))      # Write to usb

#if __name__ == '__main__':
    #cal = LinearCalibration(350, 'V', 'V')
    #port = 'COM3'

    #with PicoOutput("COM3", cal, 300) as dac:
        #print(dac.target)
        #print(dac.control)
        #while True:
            #try:
                #x = float(input('Enter a voltage (max 300): '))
            #except ValueError:
                #print('Non-numerical input found. Exiting...')
                #break
            #try:
                #dac.target = x
                #print(dac.target)
                #print(dac.control)
            #except ValueError as e:
                #print(e)