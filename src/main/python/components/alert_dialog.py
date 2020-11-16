from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class AlertDialog(QDialog):
    """
    A class to represent a Dialog box component that alerts users before a user action could be processed.

    Attributes
    ----------
    window_title - Window title of the dialog box.
    text_to_display - Text to display on dialog box.

    """
    def __init__(self, window_title, text_to_display):
        super().__init__()

        # Properties
        self.window_title = window_title
        self.text_to_display = text_to_display

        self.dialog_message_label = None
        self.buttons_to_display = None
        self.clicked_button = None
        self.layout = None

        # Instantiate relevant components
        self.configure_dialog_stylesheet()
        self.configure_buttons_to_display()
        self.configure_message_label()
        self.configure_dialog_layout()

    def exec_(self):
        """Overloads super method and returns clicked button on the dialog box."""
        super().exec_()
        return self.clicked_button

    def configure_dialog_stylesheet(self):
        self.setAutoFillBackground(True)
        self.setWindowTitle(self.window_title)
        self.setMinimumSize(400, 150)

        # Setting modal blocks any other event till the dialog is closed.
        self.setModal(True)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(51, 51, 61))
        self.setPalette(palette)

    def configure_buttons_to_display(self):
        self.buttons_to_display = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.Cancel)
        self.buttons_to_display.clicked.connect(self.handle_button_clicked_action)
        for button in self.buttons_to_display.buttons():
            button.setFont(QFont('Calibri', 13))
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

    def configure_message_label(self):
        self.dialog_message_label = QLabel()
        self.dialog_message_label.setFont(QFont('Calibri', 13))
        self.dialog_message_label.setText(self.text_to_display)

        palette = self.dialog_message_label.palette()
        palette.setColor(self.foregroundRole(), QColor(255, 255, 255))
        self.dialog_message_label.setPalette(palette)

    def configure_dialog_layout(self):
        self.layout = QGridLayout()
        self.layout.addWidget(self.dialog_message_label, 0, 0, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.buttons_to_display, 5, 0, alignment=Qt.AlignRight)
        self.setLayout(self.layout)

    def handle_button_clicked_action(self, clicked_button):
        if clicked_button == self.buttons_to_display.button(QDialogButtonBox.Yes):
            self.clicked_button = QDialogButtonBox.Yes
        elif clicked_button == self.buttons_to_display.button(QDialogButtonBox.Cancel):
            self.clicked_button = QDialogButtonBox.Cancel

        self.close()