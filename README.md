# Wien Filter Tuning - Project code
This git repo contains all code I produced for the project course at Uppsala University, Fall 22.

The current code structure puts the majority code in the installable pythion package. This package contains GUI components in its [root folder](src/pythion/), that can be used to assemble your own GUI as needed. The subfolder [interfaces](src/pythion/interfaces) contains additional classes that help with connecting the GUI to hardware components. 

Additionally, the particular GUI developed for this project is assembled in the [main.py](main.py) file. This file can be used for inspiration as to how the [pythion](src/pythion/)-package can be used in practise. Of course, if your only interested in running the GUI, then the [main.py](main.py) file is all you'll ever need. It should of course be made into an executable sooner or later, for example using `pyinstaller`.

## Getting started:
As no executable file yet exists, running the program is easiest achieved by cloning the project via `git` and installing dependencies using `pip`. To do so, make sure you have `git` installed (for example, by opening a command prompt and writing `git -v`. If you don't see a text with some version number, you need to install `git`). Also make sure to have python 3 installed (not sure which specific version is needed). A python installation can similarily be checked by running `python --version` or `python3 --version`.

Next, navigate in the command prompt to the folder where you wish to install the project, and run `git clone https://github.com/GustavLidberg/WienFilter.git`. This will add all project files to your own computer.

To install dependencies, you might want to create a virtual environment, to make sure you don't pollute your global python environment with packages. This can, for example, be achieved by writing `python -m venv ./venv` in the command prompt (make sure you're situated in the project's root folder). Then, activate the virtual environment using `source ./venv/Scripts/activate` (at least on my windows machine, you may have to locate the activation script yourself). Finally, install project dependencies by writing `pip install -e .`. Now, you should be able to run the program by writing `python main.py` or `python3 main.py`.

## Project structure
Here's how the project is (currently) structured! This might change at any time with little to no notice so be aware.
- The [Pico](Pico/) folder contains MicroPython code that's expected to run on a Raspberry Pi Pico connected to a MCP4725 Digital-Analog Converter. This code is used for serial communication with the rest of the project, in particular through the [USBConnection](src/interfaces/usb.py) class.
- The [src](src/) folder contains all project code that's expected to run on a lab computer. At some point, this folder should probably be made into an intallable package, and tests should be put separately. The python files organized directly under [src](src/) are *high-level* Qt modules. They are concerned with all the business logic related to a GUI-component. They can for example use an interface class as data model. [src](src/) also contains an entry-point script `main.py` which demonstrates how the high-level components can be assembled and connected to form a complete GUI.
- The high-level components of the [src](src) directory inherit all their graphical layout from the layout Qt classes located in the [layout](src/layout/) folder. The files in [layout](src/layout/) have not been manually edited, but are instead the result of compiling the corresponding `.ui` files located in the [xml](src/layout/xml/) subfolder. The `.ui` files, in turn, have been created using Qt Designer.
- All hardware communication is handled by classes in the [interfaces](src/interfaces/) folder. This includes abstract classes such as [`Output`](src/interfaces/output.py) which are used by the high-level GUI components, concrete implementations such as the [`PicoOutput`](src/interfaces/pico_output.py) class, and USB helpers in the [usb.py](src/interfaces/usb.py) file.

## About the Qt framework structure
This part is mostly here to preserve my own sanity working with the Qt GUI framework. It appears that the auto-generated `.py` files are *not* themselves Qt objects. Instead, they simply wrap classes that inherit from `object`. However, what these template-like objects do is to define methods (`SetupUI` and `RetranslateUi` which take a given Qt object as input, and applies the desired layout to that object).

To later consume these methods, we let the graphical component objects inherit from the templates, and then call the setup methods through a call like `self.SetupUi(self)`. Of course, inheriting from these objects does nothing more than make the methods accessible - they could just as well have been kept externally. However, the component objects do also inherit from the relevat Qt object (i.e. `QWidget` or `QMainWindow`) so that all graphical aspects are taken care of.

