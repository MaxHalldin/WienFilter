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
    def __init__(self, parent: Action, action: Callable[..., None], args: list[Any], kwargs: dict[str, Any]):
        QRunnable.__init__(self)
        self.action = action
        self.args = args
        self.kwargs = kwargs
        self.parent = parent
        self.setAutoDelete(False)

    def run(self) -> None:
        self.action(*self.args, **self.kwargs)
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
        *,
        action: Callable[..., None],
        args: list[Any],
        kwargs: dict[str, Any],
        parent: QWidget | None = None,
        text: str | None = None,
    ):
        # Boilerplate initialization
        super().__init__(parent)
        self.setupUi(self)  # type: ignore
        # Custom initialization
        self.text = 'Activate' if text is not None else text
        self.runner = CustomRunnable(self, action, args, kwargs)
        self.ready = True
        self._cancelled = False
        self.configure()

    @pyqtSlot()
    def reactivate(self) -> None:
        self.ready = True
        self._cancelled = False
        self.button.setText(self.text)

    def configure(self) -> None:
        # Set name label
        if self.text:
            self.button.setText(self.text)
        self.button.clicked.connect(self._button_pressed)  # type: ignore

    def _button_pressed(self) -> None:
        if self.ready:
            # Activate pressed
            self.ready = False
            self.button.setText('Cancel')
            self.before_execution()
            QThreadPool.globalInstance().start(self.runner)
        else:
            # Cancel pressed
            self._cancelled = True
            if QThreadPool.globalInstance().activeThreadCount():
                QThreadPool.globalInstance().waitForDone()

    def before_execution(self) -> None:
        pass
