# Wien Filter Tuning - Project code
This git repo contains all code I produced for the project course at Uppsala University, Fall 22.

This (hopefully soon) includes hardware interfaces for communication with lab equipment, a GUI and some optimization routines. Best of luck with it!

## Getting started:
For now, there's really no demo executable file.

To install dependencies, you might want to create a virtual environment, for example by writing: `python -m venv ./venv`. Then, activate the virtual environment using `source ./venv/Scripts/activate` (at least on my machine, you may have to locate the activation script yourself). Finally, install packages through `pip install -r requirements.txt`, and you should be able to run everything in the project (except the MicroPython files under `./Pico`)! When done, exit the virtual environment using `deactivate`.

## Project structure
Here's how the project is (currently) structured! This might change at any time with little to no notice so be aware.
- The [Pico](Pico/) folder contains MicroPython code that's expected to run on a Raspberry Pi Pico connected to a MCP4725 Digital-Analog Converter. This code is used for serial communication with the rest of the project, in particular through the [USBConnection](src/interfaces/usb.py) class.
- The [src](src/) folder contains all project code that's expected to run on a lab computer. At some point, this folder should probably be made into an intallable package, and tests should be put separately. The python files organized directly under [src](src/) are *high-level* Qt modules. They are concerned with all the business logic related to a GUI-component. They can for example use an interface class as data model. [src](src/) also contains an entry-point script `main.py` which demonstrates how the high-level components can be assembled and connected to form a complete GUI.
- The high-level components of the [src](src) directory inherit all their graphical layout from the layout Qt classes located in the [layout](src/layout/) folder. The files in [layout](src/layout/) have not been manually edited, but are instead the result of compiling the corresponding `.ui` files located in the [xml](src/layout/xml/) subfolder. The `.ui` files, in turn, have been created using Qt Designer.
- All hardware communication is handled by classes in the [interfaces](src/interfaces/) folder. This includes abstract classes such as [`Output`](src/interfaces/output.py) which are used by the high-level GUI components, concrete implementations such as the [`PicoOutput`](src/interfaces/pico_output.py) class, and USB helpers in the [usb.py](src/interfaces/usb.py) file.

## About the Qt framework structure
This part is mostly here to preserve my own sanity working with the Qt GUI framework. It appears that the auto-generated `.py` files are *not* themselves Qt objects. Instead, they simply wrap classes that inherit from `object`. However, what these template-like objects do is to define methods (`SetupUI` and `RetranslateUi` which take a given Qt object as input, and applies the desired layout to that object).

To later consume these methods, we let the graphical component objects inherit from the templates, and then call the setup methods through a call like `self.SetupUi(self)`. Of course, inheriting from these objects does nothing more than make the methods accessible - they could just as well have been kept externally. However, the component objects do also inherit from the relevat Qt object (i.e. `QWidget` or `QMainWindow`) so that all graphical aspects are taken care of.

