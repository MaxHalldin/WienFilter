# Wien Filter Tuning - Project code
This git repo contains all code produced for the project course at Uppsala University, Fall 22.

The current code structure puts the majority of the code in the installable [pythion](pythion) package. This package contains GUI components in its [root folder](src/pythion/), that can be used to assemble your own GUI as needed. The subpackage [connections](src/pythion/_connections) contains additional classes that help with connecting the GUI to hardware components. 

Additionally, the particular GUI developed for this project is assembled in the [main.py](main.py) file. This file can be used for inspiration as to how the [pythion](src/pythion/)-package can be used in practise. Of course, if you're only interested in running the GUI, then the [main.py](main.py) file is all you'll ever need. It should of course be made into an executable sooner or later, for example by using `pyinstaller`.

## Getting started:
Running the program is currently easiest achieved by cloning the project via `git` and installing dependencies using `pip`. To do so, make sure you have `git` installed (for example, by opening a command prompt and type `git -v`. If you don't see a text with some version number, you need to install `git`). Also make sure to have python 3 installed (for now, the project requires version 11, but this could probably be rolled back to earlier versions if needed since the modern features are only used for type hinting). A python installation can similarily be checked by running `python --version` or `python3 --version`.

Next, navigate in the command prompt to the folder where you wish to install the project, and run `git clone https://github.com/GustavLidberg/WienFilter.git`. This will add all project files to your own computer.

To install dependencies, you might want to create a virtual environment, to make sure you don't pollute your global python environment with packages. This can, for example, be achieved by writing `python -m venv ./venv` in the command prompt (make sure you're situated in the project's root folder). Then, activate the virtual environment using `source ./venv/Scripts/activate` (at least on my windows machine, you may have to locate the activation script yourself). Finally, install project dependencies by writing `pip install -e .`. Now, you should be able to run the program by writing `python main.py` or `python3 main.py`.

## Project Structure
Here's how the project is (currently) structured! This might change at any time with little to no notice so be aware.
- The [Pico](Pico/) folder is only used for documentational purposes, as it contains MicroPython code that's expected to run on a Raspberry Pi Pico connected to a MCP4725 Digital-Analog Converter. This code is used for serial communication with the rest of the project, in particular through the [USBConnection](src/_connections/usb.py) class.
- The [src](src/) folder contains the `pythion` package, an installable package for creating lab GUI's. The python files organized directly under [src/pythion](src/pythion/) are GUI *components*, that encapsulate some high-level logic and can be joined together into a complete GUI. 
- The high-level components of the [src](src) directory inherit all their graphical layout from the layout Qt classes located in the [_layout](src/_layout/) folder. The files in [_layout](src/_layout/) have not been manually edited, but are instead the result of compiling the corresponding `.ui` files located in the [xml](src/_layout/xml/) subfolder. The `.ui` files, in turn, have been created using Qt Designer.
- The subpackage [connections](src/_connections) contains many helper classes that can be used together with the GUI components to connect to different lab equipment. For example, the [OutputComponent](src/output_component.py) class takes an [Output]-class from the [connections](src/_connections) subpackage as a parameter, and uses it as its data model.
- The only script to be run on the lab computer outside [src](src/) is the entry-point script [main.py](main.py) which demonstrates how the `pythion` package can be used to assemble and connect a GUI.

## About the Qt framework structure
These paragraphs are mostly here to preserve my own sanity working with the Qt GUI framework. It appears that the auto-generated `.py` files are *not* themselves Qt objects. Instead, they simply wrap classes that inherit from `object`. What these template-like objects do is to define methods (`SetupUI` and `RetranslateUi` which take a given Qt object as input, and applies the desired layout to that object).

To later consume these methods, we let the graphical component objects inherit from the templates, and then call the setup methods through a call like `self.SetupUi(self)`. Of course, inheriting from these objects does nothing more than make the methods accessible - they could just as well have been kept externally. However, the component objects do also inherit from the relevat Qt object (i.e. `QWidget` or `QMainWindow`) so that all graphical aspects are taken care of.

# Developing
In order to continue developing the project, you could use a little more configuration. First, you might want to create another virtual environvent to install the dev-dependencies needed for linting and testing. This can for example be achieved by `python -m venv ./devenv`, followed by `source ./devenv/Scripts/activate`. Installations are achieved by running `pip install -e .` again, then followed by `pip install -r requirements_dev.txt`. You should then be able to run type-hinting checks by running `mypy src`, linting with `flake8 src` and testing with `pytest`.

If you want to design new UI-components, do so by creating a `QWidget` object in Qt Designer and save it as a `.ui` file in the [xml](src/pythion/_layout/xml/) folder. If it automatically saves a `.py` file as well, you can just drag this file to the [_layout](src/pythion/_layout/) folder and you're good to go! To use your new design in the code, you should create a component file in the [pythion](src/pythion/) directory that inherits from your layout file - look at the other components to get a feel for how it's done. This file is where all logic and data models for the component should go. Finally, if you want to be able to use your new component with a package import like `from pythion import ...`, you also need to add an import reference to your new component in the package [__init__.py](src/pythion/__init__.py) file. 

If a `.py` file is *not* automatically generated by your Qt Designer, you need to install `pyqt5-tools`. To do so, I had to roll back to python version 9, for unknown reasons. If you also need to do this, do so by installing python 9 and ensure it's the active python interpreter for your terminal. Then, run for example `python -m venv ./qtenv`, then `source ./qtenv/Scripts/activate`, then `pip install pyqt5` and finally `qtenv/Scripts/pip.exe install pyqt5-tools~=5.15` (the last version number should match the just installed version of `pyqt5`). Then, you should be able to manually compile your component by writing `pyuic ./src/pythion/_layout/<your-component-name>.py ./src/pythion/_layout/xml/<your-component-name>.ui`.

## A little on USB connections:
This is how I intend for USB connections to be managed in the program.

In order to ensure that all open connectins will be closed on exit, a "master" `with` clause will be needed. This is achieved by letting the `Input` and `Output` components implement `__enter__`/`__exit__`, and calling `app.run()` from within a with statement.

However, since ports must sometimes be designated at runtime, the connections can't be opened by the time `__enter__` is called. Instead, the `Input` and `Output` classes should implement a graphical interface to select a port. The configuration settings for this port selection are *not* set on this class, however. Instead, the logic is as following:

The GUI `Input`/`Output` components hold references to `InputInterface`/`OutputInterface` classes from `pythion.connections`. A port selection option should only be made available *if* the interface class is a subclass of `USBConnection`. Therefore, it's reasonable for the `Input`/`Output` class to make an `isinstance`-check to the interface, and see whether port selection should be initiated. Furthermore, the specifics of port selection should be governed by the USBConnection class itself, possibly with settings injected by the interface subclass.


