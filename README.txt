# Wien Filter Tuning - Project code
This git repo contains all code I produced for the project course at Uppsala University, Fall 22.

This (hopefully soon) includes hardware interfaces for communication with lab equipment, a GUI and some optimization routines. Best of luck with it!

## Getting started:
For now, there's really no demo executable file.

To install dependencies, you might want to create a virtual environment, for example by writing: `python -m venv ./venv`. Then, activate the virtual environment using `source ./venv/Scripts/activate` (at least on my machine, you may have to locate the activation script yourself). Finally, install packages through `pip install -r requirements.txt`, and you should be able to run everything in the project (except the MicroPython files under `./Pico`)! When done, exit the virtual environment using `deactivate`.