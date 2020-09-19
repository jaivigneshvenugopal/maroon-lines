import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import qutepart


class UI(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.file_path = None
        self.configure_frame()
        self.configure_menubar()
        self.configure_editor()
        self.show()

    def configure_menubar(self):
        self._menubar = self.menuBar()
        self.__file = self._menubar.addMenu('File')
        self.___new = self.__file.addAction('New')
        self.___new.setShortcut("Ctrl+N")
        self.___open = self.__file.addAction('Open')
        self.___open.setShortcut("Ctrl+O")
        self.___save = self.__file.addAction('Save')
        self.___save_as = self.__file.addAction('Save As...')
        self.___save_as.setShortcut("Ctrl+S")
        self.___exit = self.__file.addAction('Exit')

        self.configure_menubar_connections()

    def configure_menubar_connections(self):
        self.___save_as.triggered.connect(self.handle_save_as_action)
        self.___open.triggered.connect(self.handle_open_action)

    def handle_open_action(self):
        file_info = QFileDialog.getOpenFileName(self, 'Open File')
        name, file_type = file_info[0], file_info[1]
        if name != '':
            self.file_path = name
            file = open(name, 'r')
            with file:
                text = file.read()
                self.editor.text = text

    def handle_save_as_action(self):
        file_info = QFileDialog.getSaveFileName(self, 'Save As...')
        name, file_type = file_info[0], file_info[1]

        if name != '':
            text = self.editor.textForSaving()
            file = open(name[0], 'w')
            file.write(text)
            file.close()

    # Define the geometry of the main window
    def configure_frame(self):
        self.setGeometry(500, 250, 1000, 500)
        self.setWindowTitle("Maroon Lines")

    # Instantiate editor
    def configure_editor(self):
        self.editor = qutepart.Qutepart()
        self.editor.currentLineColor = None
        self.editor.drawIncorrectIndentation = False
        self.editor.setFont(QFont('Fire Code', 14))
        self.setCentralWidget(self.editor)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ui = UI()
    sys.exit(app.exec_())
