from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class AlertDialog(QDialog):
    def __init__(self, text):
        super().__init__()

        # Properties
        self.label = QLabel()
        self.layout = QGridLayout()
        self.button_role = None
        self.button_set = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.Cancel)

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
        self.label.setText('Are you sure about clearing your file history?')

        font = self.label.font()
        self.label.setFont(font)

        palette = self.label.palette()
        palette.setColor(self.foregroundRole(), QColor(255, 255, 255))
        self.label.setPalette(palette)

    def configure_button_set(self):
        self.button_set.clicked.connect(self.handle_button_action)
        for button in self.button_set.buttons():
            button.setFont(QFont())
            button.setIcon(QIcon())
            button.setStyleSheet("""
                QPushButton { 
                    background-color: #fcfcfc;
                    border-color: #000000;
                    outline: none;
                    border-radius: 6px;
                    padding: 6px;
                }

                QPushButton:focus { 
                    background-color: #f0b034;
                    border-color: #f0b034;
                    outline: none;  
                    border-radius: 6px;
                }

                QPushButton:hover { 
                    background-color: #f0b034;
                    border-color: #f0b034;
                    outline: none;
                    border-radius: 6px;
                }

        """)

    def configure_dialog_style(self, text):
        self.setAutoFillBackground(True)
        self.setWindowTitle(text)
        self.setModal(True)
        self.setMinimumSize(400, 150)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(51, 51, 61))
        self.setPalette(palette)

    def handle_button_action(self, clicked_button):
        if clicked_button == self.button_set.button(QDialogButtonBox.Yes):
            self.button_role = QDialogButtonBox.Yes
        elif clicked_button == self.button_set.button(QDialogButtonBox.Cancel):
            self.button_role = QDialogButtonBox.Cancel
        self.close()

    def exec_(self):
        super().exec_()
        return self.button_role
