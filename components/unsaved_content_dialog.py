from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class UnsavedContentDialog(QDialog):
    """
    A class to represent a Dialog box component that questions users about unsaved content
    before a action could be processed.

    Attributes
    ----------
    window_title - Window title of the dialog box.
    text_to_display - Text to display on dialog box.
    close_window - Boolean that indicates if application should be closed after the dialog box is processed.

    """

    def __init__(self, window_title, text_to_display, close_window=False):
        super().__init__()

        # Properties
        self.window_title = window_title
        self.text_to_display = text_to_display
        self.close_window = close_window

        self.dialog_message_label = None
        self.layout = None
        self.clicked_button = None
        self.buttons_to_display = None

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
        if self.close_window:
            self.buttons_to_display = QDialogButtonBox(QDialogButtonBox.Save |
                                                       QDialogButtonBox.Cancel |
                                                       QDialogButtonBox.Close)
        else:
            self.buttons_to_display = QDialogButtonBox(QDialogButtonBox.Save |
                                                       QDialogButtonBox.Ignore)

        self.buttons_to_display.clicked.connect(self.handle_button_clicked_action)
        for button in self.buttons_to_display.buttons():
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

    def configure_message_label(self):
        self.dialog_message_label = QLabel()
        self.dialog_message_label.setText(self.text_to_display)

        font = self.dialog_message_label.font()
        self.dialog_message_label.setFont(font)

        palette = self.dialog_message_label.palette()
        palette.setColor(self.foregroundRole(), QColor(255, 255, 255))
        self.dialog_message_label.setPalette(palette)

    def configure_dialog_layout(self):
        self.layout = QGridLayout()
        self.layout.addWidget(self.dialog_message_label, 0, 0, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.buttons_to_display, 5, 0, alignment=Qt.AlignRight)
        self.setLayout(self.layout)

    def handle_button_clicked_action(self, clicked_button):
        if clicked_button == self.buttons_to_display.button(QDialogButtonBox.Save):
            self.clicked_button = QDialogButtonBox.Save
        elif clicked_button == self.buttons_to_display.button(QDialogButtonBox.Cancel):
            self.clicked_button = QDialogButtonBox.Cancel
        elif clicked_button == self.buttons_to_display.button(QDialogButtonBox.Close):
            self.clicked_button = QDialogButtonBox.Close
        elif clicked_button == self.buttons_to_display.button(QDialogButtonBox.Ignore):
            self.clicked_button = QDialogButtonBox.Ignore

        self.close()
