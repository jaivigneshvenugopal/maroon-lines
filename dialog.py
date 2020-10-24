from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Dialog(QDialog):
    def __init__(self, text):
        super().__init__()

        # Properties
        self.label = QLabel()
        self.button_role = None
        self.button_set = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel | QDialogButtonBox.Close)
        self.layout = QGridLayout()

        # Instantiate relevant components
        self.configure_dialog_style(text)
        self.configure_button_set()
        self.configure_message_label()
        self.configure_dialog_layout()

    def configure_dialog_layout(self):
        self.layout.addWidget(self.label, 0, 0, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.button_set, 5, 0, alignment=Qt.AlignRight)
        self.setLayout(self.layout)

    def configure_message_label(self):
        self.label.setText('Do you want to save your changes?')

        font = self.label.font()
        font.setBold(True)
        self.label.setFont(font)

        palette = self.label.palette()
        palette.setColor(self.foregroundRole(), QColor(205, 211, 215))
        self.label.setPalette(palette)

    def configure_button_set(self):
        self.button_set.clicked.connect(self.handle_button_action)

    def configure_dialog_style(self, text):
        self.setAutoFillBackground(True)
        self.setWindowTitle(text)
        self.setModal(True)
        self.setMinimumSize(400, 150)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(51, 51, 61))
        self.setPalette(palette)

    def handle_button_action(self, clicked_button):
        if clicked_button == self.button_set.button(QDialogButtonBox.Save):
            self.button_role = QDialogButtonBox.Save
        elif clicked_button == self.button_set.button(QDialogButtonBox.Cancel):
            self.button_role = QDialogButtonBox.Cancel
        elif clicked_button == self.button_set.button(QDialogButtonBox.Close):
            self.button_role = QDialogButtonBox.Close
        else:
            raise Exception('Dialog was not closed properly')
        self.close()

    def exec_(self):
        super().exec_()
        return self.button_role
