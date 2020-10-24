from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class MenuBar(QMenuBar):
    def __init__(self):
        super().__init__()
        self.installEventFilter(self)
        self.setStyleSheet("""
            QMenuBar {
                background-color: rgb(51, 51, 61);
                color: rgb(205,215,211);
                font: 17px;
                min-height: 35px;
            }

            QMenuBar::item {
                background-color: rgb(51, 51, 61);
                color: rgb(205,215,211);
                margin: 0px;
            }

            QMenuBar::item::selected {
                background-color: rgb(60, 60, 60);
            }
        """)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyRelease and event.modifiers() == Qt.AltModifier:
            return True
        return False


