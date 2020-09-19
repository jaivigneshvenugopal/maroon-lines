import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import qutepart


class UI(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.configure_frame()
        self.configure_menubar()
        self.configure_editor()
        self.show()

    def configure_menubar(self):
        self._menubar = self.menuBar()
        self.__file = self._menubar.addMenu('File')
        self.___new = self.__file.addAction('New')
        self.___open = self.__file.addAction('Open')
        self.___save = self.__file.addAction('Save')
        self.___save_as = self.__file.addAction('Save As...')
        self.___exit = self.__file.addAction('Exit')

        self.configure_menubar_connections()

    def configure_menubar_connections(self):
        self.___save.triggered.connect(self.handle_save_action)

    def handle_save_action(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')
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
