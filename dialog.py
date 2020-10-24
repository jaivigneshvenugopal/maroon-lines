from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Dialog(QDialog):
    def __init__(self, text):
        super().__init__()

        self.button_role = None
        self.button_set = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel | QDialogButtonBox.Close)
        self.button_set.clicked.connect(self.handle_button_action)

        self.layout = QGridLayout()
        self.layout.addWidget(QLabel('Do you want to save your changes?'), 0, 0, 5, 3, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.button_set, 5, 0, 1, 3)

        self.setWindowTitle(text)
        self.setModal(True)
        self.setLayout(self.layout)
        self.setMinimumSize(400, 150)

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
