import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from graph_visualization import GraphVisualization
import control
from editor import Editor
from IPython import embed


class MenuBar(QMenuBar):
    def __init__(self):
        super().__init__()
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyRelease and event.modifiers() == Qt.AltModifier:
            return True
        return False


class MaroonLines(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()

        # File-related properties
        self.file_path = None
        self.file_hash = None

        # Widget-related properties
        self.layout = None
        self.central_widget = None
        self.menu_bar = MenuBar()
        self.editor = Editor()
        self.graph = GraphVisualization()
        self.status_bar = QStatusBar()
        self.status_bar_right_corner_label = None

        # Shortcuts and corresponding functions
        self.shortcut_arrow_functions = {
            Qt.Key_Up: self.graph.move_up,
            Qt.Key_Down: self.graph.move_down,
            Qt.Key_Right: self.graph.move_right,
            Qt.Key_Left: self.graph.move_left
        }

        # Instantiate relevant components
        self.configure_layout_and_central_widget()
        self.configure_menu_bar()
        self.configure_editor()
        self.configure_graph()
        self.configure_status_bar()
        self.configure_and_show_frame()

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and event.modifiers() == Qt.AltModifier:
            key = event.key()
            if key in self.shortcut_arrow_functions:
                traverse = self.shortcut_arrow_functions[key]
                traverse()
                return True
            else:
                return False
        return False

    def configure_menu_bar(self):
        self.setMenuBar(self.menu_bar)
        self.menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: rgb(51, 51, 61);
                color: rgb(205,215,211);
                font: 16px;
            }

            QMenuBar::item {
                background-color: rgb(51, 51, 61);
                color: rgb(205,215,211);
            }

            QMenuBar::item::selected {
                background-color: rgb(60, 60, 60);
            }
        """)

        menu = self.menu_bar.addMenu('File')

        new_action = menu.addAction('New')
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.handle_new_action)

        open_action = menu.addAction('Open')
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.handle_open_action)

        save_action = menu.addAction('Save')
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.handle_save_action)

        save_as_action = menu.addAction('Save As...')
        save_as_action.setShortcut("Shift+Ctrl+S")
        save_as_action.triggered.connect(self.handle_save_as_action)

        exit_action = menu.addAction('Exit')
        exit_action.setShortcut("Ctrl+W")
        exit_action.triggered.connect(self.handle_exit_action)

    def configure_status_bar(self):
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: rgb(51, 51, 61);
                color: rgb(205,215,211);
                font: 16px;
            }
        """)
        self.editor.textChanged.connect(self.set_number_of_lines_and_versions)
        self.status_bar_right_corner_label = QLabel()
        self.status_bar_right_corner_label.setStyleSheet("""
            QLabel {
                color: rgb(205,215,211)
            }
        """)
        self.status_bar.addPermanentWidget(self.status_bar_right_corner_label)

    def handle_new_action(self):
        self.file_path = None
        self.file_hash = None
        self.editor.clear()
        self.graph.render_graph(None)
        num_versions = self.graph.curr_num_nodes
        self.status_bar_right_corner_label.setText('Versions: {}'.format(num_versions))

    def handle_open_action(self):
        file_info = QFileDialog.getOpenFileName(self, 'Open File')
        name, file_type = str(file_info[0]), file_info[1]
        if name != '':
            self.file_path = name
            if control.repo_exists(self.file_path):
                self.file_hash = control.get_current_file_hash(self.file_path)
                self.graph.render_graph(control.repo_index(self.file_path))
            with open(name, 'r', encoding="utf8") as f:
                text = f.read()
                self.editor.text = text
            num_versions = self.graph.curr_num_nodes
            self.status_bar_right_corner_label.setText('Versions: {}'.format(num_versions))

    def handle_save_action(self):
        if self.file_path:
            data = self.editor.textForSaving()
            with open(self.file_path, 'w', encoding="utf8") as f:
                f.write(data)
                file_hash = control.get_hash(data)
                if control.append_object(self.file_path, file_hash, data, self.file_hash):
                    self.file_hash = file_hash
                    self.graph.render_graph(control.repo_index(self.file_path))
        else:
            self.handle_save_as_action()
        num_versions = self.graph.curr_num_nodes
        self.status_bar_right_corner_label.setText('Versions: {}'.format(num_versions))

    def handle_save_as_action(self):
        file_info = QFileDialog.getSaveFileName(self, 'Save As...')
        name, file_type = str(file_info[0]), file_info[1]
        if name != '':
            self.file_path = name
            text = self.editor.textForSaving()
            with open(name, 'w', encoding="utf8") as f:
                f.write(text)
            control.repo_init(self.file_path)
            self.file_hash = control.get_current_file_hash(self.file_path)
            self.graph.render_graph(control.repo_index(self.file_path))

    def handle_exit_action(self):
        sys.exit()

    def handle_setting_node(self, file_hash):
        control.set_object(self.file_path, file_hash)
        self.file_hash = file_hash
        self.editor.text = control.read_repo_object(self.file_path, file_hash)
        with open(self.file_path, 'w', encoding="utf8") as f:
            f.write(self.editor.text)

    # Define the geometry of the application and show it
    def configure_and_show_frame(self):
        self.setGeometry(500, 250, 1000, 500)
        self.setWindowTitle("Maroon Lines")
        self.showMaximized()

    # Define layout and set a central widget to QMainWindow
    def configure_layout_and_central_widget(self):
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background-color: #f0b034")
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    # Instantiate editor
    def configure_editor(self):
        self.editor.currentLineColor = None
        self.editor.drawIncorrectIndentation = False
        self.editor.moveLineUpAction.setEnabled(False)
        self.editor.moveLineDownAction.setEnabled(False)
        self.editor.setStyleSheet("background-color: #fcfcfc")
        self.editor.setFont(QFont('Fire Code', 14))
        self.configure_editor_scrollbar()
        editor_margin = self.editor.getMargins()[0]
        font = QFont('Fire Code', 14)
        font.setItalic(True)
        editor_margin.setFont(font)
        editor_margin.setStyleSheet('background-color: #f0f0f0')
        self.layout.addWidget(self.editor, 8)
        self.editor.installEventFilter(self)

    def configure_graph(self):
        self.graph.current_node.connect(self.handle_setting_node)
        self.layout.addWidget(self.graph, 2)
        self.graph.render_graph(None)

    def configure_editor_scrollbar(self):
        scroll_bar = self.editor.verticalScrollBar()
        scroll_bar.setStyleSheet(
            """QScrollBar:vertical {
                    width: 11px;
                    margin: 0;
                    background: #fcfcfc;
                  }

                  QScrollBar::handle:vertical {
                    border: 11px solid #d9d9d9;
                    background: #33333d;
                    min-height: 10px;
                  }

                  QScrollBar::add-line:vertical {
                    height: 0px;
                  }

                  QScrollBar::sub-line:vertical {
                    height: 0px;
                  }

                  QScrollBar::up-arrow:vertical {
                    border: none;
                    height: 0px; 
                    width: 0px;
                    background: none;
                    color: none;
                  }

                  QScrollBar::down-arrow:vertical {
                    border: none;
                    height: 0px; 
                    width: 0px;
                    background: none;
                    color: none;                              
                  }
                  QScrollBar::add-page:vertical {
                    height: 0px; 
                  }
                  QScrollBar::sub-page:vertical {
                    height: 0px; 
                  }""")

    def set_number_of_lines_and_versions(self):
        num_lines = len(self.editor.lines)
        self.status_bar.showMessage('Lines: {}'.format(num_lines))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ml = MaroonLines()
    sys.exit(app.exec_())
