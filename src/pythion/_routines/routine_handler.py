from __future__ import annotations
from typing import Any, Callable, TYPE_CHECKING
import logging

from PyQt5.QtCore import pyqtSlot, QThreadPool
from PyQt5.QtWidgets import QWidget

if TYPE_CHECKING:
    from pythion._routines.routine import Routine

logger = logging.getLogger('pythion')


class RoutineHandler(QWidget):
    """
    The intention of this class is to provide a way for asynchronously running routines to
    run small chunks of code on the main thread, that are not related to other widgets
    (such as setting the value of an output)

    To do this, this class
    """
    routine: Routine
    ready: bool
    function: Callable[..., None] | None
    args: list[Any]
    kwargs: dict[str, Any]

    def __init__(self, routine: Routine, parent: QWidget):
        super().__init__(parent)
        routine.set_handler(self)
        self.routine = routine
        self.function = None
        self.args = []
        self.kwargs = {}
        self.ready = True

    def set_function(self, function: Callable[..., None], *args, **kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def start(self):
        if self.ready:
            # Let's go!
            self.ready = False
            QThreadPool.globalInstance().start(self.runner)

    def cancel(self):
        """
        Set cancel flag and wait for routine to exit
        """
        if not self.ready:
            self._cancelled = True
            if QThreadPool.globalInstance().activeThreadCount():
                QThreadPool.globalInstance().waitForDone()

    @pyqtSlot()
    def main_thread_execute(self):
        if self.function is None:
            logger.exception('RoutineHandler: cannot run function - no function has been provided')
        self.function(*self.args, **self.kwargs)
