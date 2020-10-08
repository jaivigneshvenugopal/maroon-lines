import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from graph import PrettyWidget
import qutepart
import control


class UI(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.file_path = None
        self.current_file_hash = None

        self.layout = None
        self.editor = None
        self.graph = PrettyWidget()

        self.configure_frame()
        self.configure_layout()
        self.configure_menubar()
        self.configure_editor()
        self.configure_graph()
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
            if control.repo_exists(self.file_path):
                self.current_file_hash = control.get_current_file_hash(self.file_path)
                self.graph.render_graph(control.repo_index(self.file_path))
            with open(name, 'r', encoding="utf8") as f:
                text = f.read()
                self.editor.text = text

    def handle_save_action(self):
        if self.file_path:
            data = self.editor.textForSaving()
            with open(self.file_path, 'w', encoding="utf8") as f:
                f.write(data)
                file_hash = control.get_hash(data)
                if control.append_object(self.file_path, file_hash, data, self.current_file_hash):
                    self.current_file_hash = file_hash
                    self.graph.render_graph(control.repo_index(self.file_path))
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
            control.repo_init(self.file_path)
            self.current_file_hash = control.get_current_file_hash(self.file_path)
            self.graph.render_graph(control.repo_index(self.file_path))

    def handle_exit_action(self):
        sys.exit()

    def handle_setting_node(self, file_hash):
        control.set_object(self.file_path, file_hash)
        self.current_file_hash = file_hash
        self.editor.text = control.read_repo_object(self.file_path, file_hash)
        with open(self.file_path, 'w', encoding="utf8") as f:
            f.write(self.editor.text)

    # Define the geometry of the main window
    def configure_frame(self):
        self.setGeometry(500, 250, 1000, 500)
        self.setWindowTitle("Maroon Lines")

    def configure_layout(self):
        self.layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

    # Instantiate editor
    def configure_editor(self):
        self.editor = qutepart.Qutepart()
        self.editor.currentLineColor = None
        self.editor.drawIncorrectIndentation = False
        self.editor.setFont(QFont('Fire Code', 14))
        self.layout.addWidget(self.editor)

    def configure_graph(self):
        self.graph.current_node.connect(self.handle_setting_node)
        self.layout.addWidget(self.graph)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ui = UI()
    sys.exit(app.exec_())
