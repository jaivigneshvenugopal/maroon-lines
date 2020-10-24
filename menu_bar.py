from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class MenuBar(QMenuBar):
    def __init__(self):
        super().__init__()
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyRelease and event.modifiers() == Qt.AltModifier:
            return True
        return False


