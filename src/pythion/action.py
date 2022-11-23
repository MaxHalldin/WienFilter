from __future__ import annotations
from typing import Any, Callable

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QMetaObject, Qt, Q_ARG, pyqtSlot, QRunnable, QThreadPool
from pythion._layout.ui_action import Ui_Action


class GUIUpdater:
    """
    This tiny helper class defines only one method:
    update can be used by an asynchronous function to update GUI components!
    """
    @staticmethod
    def update(widget: QWidget, slot: str, *args: Any) -> None:
        QMetaObject.invokeMethod(widget, slot, Qt.QueuedConnection, *[Q_ARG(type(arg), arg) for arg in args])  # type: ignore


class CustomRunnable(QRunnable):
    def __init__(self, parent: Action, action: Callable[..., None], args: Any):
        QRunnable.__init__(self)
        self.action = action
        self.args = args
        self.parent = parent
        self.setAutoDelete(False)

    def run(self) -> None:
        self.action(*self.args)
        GUIUpdater.update(self.parent, 'reactivate')


class Action(QWidget, Ui_Action):
    """
    This class has two main purposes:
        - It's a gui component with a button that initiates the process.
        - It enables running the process concurrently in the background.

    Async operation with pyqt5 is not obvious. That's why this class encapsulates a QRunnable
    instance, and uses signal emission to update the GUI between threads.
    """
    def __init__(
        self,
        action: Callable[..., None],
        *args: Any,
        parent: QWidget | None = None,
        text: str | None = None,

    ):
        # Boilerplate initialization
        super().__init__(parent)
        self.setupUi(self)  # type: ignore
        # Custom initialization
        self.text = 'Activate' if text is not None else text
        self.runner = CustomRunnable(self, action, args)
        self.ready = True
        self.configure()

    @pyqtSlot()
    def reactivate(self) -> None:
        self.ready = True
        self.button.setEnabled(True)

    def configure(self) -> None:
        # Set name label
        if self.text:
            self.button.setText(self.text)
        self.button.clicked.connect(self._start)  # type: ignore

    def _start(self) -> None:
        if self.ready:
            self.ready = False
            self.button.setEnabled(False)
            QThreadPool.globalInstance().start(self.runner)
            print('Carrying on...')