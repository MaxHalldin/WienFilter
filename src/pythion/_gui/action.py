from __future__ import annotations
from datetime import datetime
from PyQt5.QtWidgets import QWidget

from pythion._gui.layout.ui_action import Ui_Action
from pythion._routines.routine_handler import RoutineHandler
from pythion._routines.routine import Routine


class Action(RoutineHandler, Ui_Action):
    """
    This UI component represents a button which initiates some type of Action,
    by starting an asynchronous routine on a background thread. The the layout
    is imported from the Ui_Action parent class, while most of the 
    This class has two main purposes:
        - It's a gui component with a button that initiates the process.
        - It enables running the process concurrently in the background.

    Async operation with pyqt5 is not obvious. That's why this class encapsulates a QRunnable
    instance, and uses signal emission to update the GUI between threads.
    """
    def __init__(
        self,
        *,
        routine: Routine,
        parent: QWidget | None = None,
        text: str | None = None,
    ):
        # Boilerplate initialization
        super().__init__(routine, parent)
        self.setupUi(self)  # type: ignore
        # Custom initialization
        self.text = 'Activate' if text is None else text
        self.configure()

    def on_reset(self) -> None:
        self.button.setText(self.text)
        self._finished_time = datetime.now()
        self.finishedLabel.setText(f'Finished at {self._finished_time.strftime("%H:%M:%S")}')

    def on_start(self) -> None:
        self.button.setText('Cancel')
        self._starttime = datetime.now()
        self.initiatedLabel.setText(f'Started at {self._starttime.strftime("%H:%M:%S")}')
        self.finishedLabel.setText('')

    def configure(self) -> None:
        # Set name label
        if self.text:
            self.button.setText(self.text)
        self.button.clicked.connect(self._button_pressed)  # type: ignore

    def _button_pressed(self) -> None:
        if self.ready:
            # Activate pressed
            self.start()
        else:
            self.cancel()
