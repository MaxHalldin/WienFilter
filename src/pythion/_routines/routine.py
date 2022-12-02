from typing import Any, Callable

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, Q_ARG, QMetaObject, QRunnable


class Routine(QRunnable):
    tasks: list[tuple[Callable[..., None], list[Any], dict[str, Any]]]

    def __init__(self):
        QRunnable.__init__(self)
        self.setAutoDelete(False)
        self.tasks = []

    def update_widget(widget: QWidget, slot: str, *args: Any, block: bool = False) -> None:
        connection = Qt.BlockingQueuedConnection if block else Qt.QueuedConnection
        QMetaObject.invokeMethod(widget, slot, connection, *[Q_ARG(type(arg), arg) for arg in args])  # type: ignore

    def run(self) -> None:
        for task, args, kwargs in self.tasks:
            task(*args, **kwargs)

    def add_task(self, task, *args, **kwargs):
        self.tasks.append(task, args, kwargs)
