import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import qutepart
import marooncontrol


class UI(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.file_path = None
        self.current_file_hash = None
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
        self.___save.setShortcut("Ctrl+S")
        self.___save_as = self.__file.addAction('Save As...')
        self.___exit = self.__file.addAction('Exit')
        self.___exit.setShortcut("Ctrl+W")

        self.configure_menubar_connections()

    def configure_menubar_connections(self):
        self.___new.triggered.connect(self.handle_new_action)
        self.___open.triggered.connect(self.handle_open_action)
        self.___save.triggered.connect(self.handle_save_action)
        self.___save_as.triggered.connect(self.handle_save_as_action)
        self. ___exit.triggered.connect(self.handle_exit_action)

    def handle_new_action(self):
        self.file_path = None
        self.editor.clear()

    def handle_open_action(self):
        file_info = QFileDialog.getOpenFileName(self, 'Open File')
        name, file_type = str(file_info[0]), file_info[1]
        if name != '':
            self.file_path = name
            file = open(name, 'r', encoding="utf8")
            with file:
                text = file.read()
                self.editor.text = text
                file.close()

    def handle_save_action(self):
        if self.file_path:
            text = self.editor.textForSaving()
            with open(self.file_path, 'w', encoding="utf8") as f:
                f.write(text)
                file_hash = marooncontrol.get_hash(text)
                marooncontrol.append_object(self.file_path, file_hash, self.current_file_hash)
                self.current_file_hash = file_hash
        else:
            self.handle_save_as_action()

    def handle_save_as_action(self):
        file_info = QFileDialog.getSaveFileName(self, 'Save As...')
        name, file_type = str(file_info[0]), file_info[1]
        if name != '':
            self.file_path = name
            text = self.editor.textForSaving()
            with open(name, 'w', encoding="utf8") as f:
                f.write(text)
            marooncontrol.repo_init(self.file_path)
            self.current_file_hash = marooncontrol.get_current_file_hash(self.file_path)


    def handle_exit_action(self):
        sys.exit()

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
