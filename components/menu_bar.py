from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class MenuBar(QMenuBar):
    """
    Menu bar has similar properties to its inherited class, but with a change in stylesheet
    and event filter functionality.

    """
    def __init__(self):
        super().__init__()
        self.installEventFilter(self)
        self.setStyleSheet("""
            QMenuBar {
                background-color: rgb(51, 51, 61);
                color: rgb(205,215,211);
                spacing: 0px;
                font: 17px;
                min-height: 35px;
            }

            QMenuBar::item {
                background-color: rgb(51, 51, 61);
                color: rgb(205,215,211);
                spacing: 0px;
                font: 17px;
                min-height: 35px;

                padding-left: 10px;
                padding-right: 10px;
            }

            QMenuBar::item::selected {
                background-color: rgb(60, 60, 60);
                color: rgb(205,215,211);
                spacing: 0px;
                font: 17px;
                min-height: 35px;
                
                padding-left: 10px;
                padding-right: 10px;
            }
        """)

    def eventFilter(self, source, event):
        """
        Menu bar has this ability to focus on itself with an Alt Keypress event. This feature is disabled here
        due to a clash of functionality.

        :param source:
        :param event:
        :return:
        """
        if event.type() == QEvent.KeyRelease and event.modifiers() == Qt.AltModifier:
            return True

        return False


