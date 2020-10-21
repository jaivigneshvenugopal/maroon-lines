import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from timeline import Timeline
from repository_control_utils import *
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

        # Repo-related properties
        self.index = None

        # Widget-related properties
        self.layout = QHBoxLayout()
        self.central_widget = QWidget()
        self.menu_bar = MenuBar()
        self.editor = Editor()
        self.graph = Timeline()
        self.status_bar = QStatusBar()

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
        self.configure_status_bar()
        self.configure_editor()
        self.configure_graph()
        self.configure_and_show_frame()

    # Event filter for Editor to ignore certain shortcuts pertaining to Graph
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

    # Define layout and set a central widget to QMainWindow
    def configure_layout_and_central_widget(self):
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setStyleSheet("background-color: #f0b034")
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    # Refactored
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

    # Refactored
    def configure_status_bar(self):
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: rgb(51, 51, 61);
                color: rgb(205,215,211);
                font: 16px;
            }
        """)
        right_corner_label = QLabel()
        right_corner_label.setStyleSheet("""
            QLabel {
                color: rgb(205,215,211)
            }
        """)
        self.status_bar.addPermanentWidget(right_corner_label)
        self.update_status_bar_num_lines()

    # Refactored
    def configure_graph(self):
        self.graph.curr_node_changed.connect(self.load_repo_file)
        self.graph.num_nodes_changed.connect(self.update_status_bar_num_nodes)
        self.layout.addWidget(self.graph, 18)
        self.graph.render_graph(index=None)

    # Define the geometry of the application and show it
    def configure_and_show_frame(self):
        self.setGeometry(500, 250, 1000, 500)
        self.setWindowTitle("Maroon Lines")
        self.showMaximized()

    # Refactored
    def handle_new_action(self):
        self.update_file_path_and_hash(file_path=None)
        self.editor.clear()
        self.graph.render_graph(index=None)

    # Refactored
    def handle_open_action(self):
        file_info = QFileDialog.getOpenFileName(self, 'Open File')
        file_path, file_type = str(file_info[0]), file_info[1]
        if file_path:
            self.load_file(file_path)
            self.update_file_path_and_hash(file_path)
            self.instantiate_index()
            self.graph.render_graph(repo_index(self.file_path))

    # Refactored
    def handle_save_action(self):
        if not self.file_path:
            self.handle_save_as_action()
        else:
            file_hash = get_hash(self.editor.text)
            if repo_object_exists(self.file_path, file_hash):
                update_repo_index_curr_object(self.file_path, file_hash)
            else:
                append_repo_object(self.file_path, file_data=self.editor.text, parent_file_hash=self.file_hash)
                self.store_file(self.file_path)

            self.file_hash = file_hash
            self.graph.render_graph(repo_index(self.file_path))

    # Refactored
    def handle_save_as_action(self):
        file_info = QFileDialog.getSaveFileName(self, 'Save As...')
        file_path, file_type = str(file_info[0]), file_info[1]
        if file_path:
            self.store_file(file_path)
            if self.new_file_built_upon_existing_one(file_path):
                self.port_existing_repo_to_new_path(file_path)
            self.update_file_path_and_hash(file_path)
            self.instantiate_index()
            self.graph.render_graph(repo_index(self.file_path))

    # Refactored
    def handle_exit_action(self):
        sys.exit()

    # Instantiate editor
    def configure_editor(self):
        # Configure editor settings
        self.editor.currentLineColor = None
        self.editor.drawIncorrectIndentation = False
        self.editor.moveLineUpAction.setEnabled(False)
        self.editor.moveLineDownAction.setEnabled(False)

        # Configure editor style
        self.editor.setStyleSheet("background-color: #fcfcfc")
        self.editor.setFont(QFont('Fire Code', 14))

        # Configure editor scroll bar
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

        # Configure editor margins
        editor_margin = self.editor.getMargins()[0]
        font = QFont('Fire Code', 14)
        editor_margin.setFont(font)
        editor_margin.setStyleSheet('background-color: #f0f0f0')

        self.editor.textChanged.connect(self.update_status_bar_num_lines)
        self.editor.installEventFilter(self)
        self.layout.addWidget(self.editor, 82)

    # Slot Functions
    def update_status_bar_num_lines(self):
        self.status_bar.showMessage('Lines: {}'.format(len(self.editor.lines)))

    def update_status_bar_num_nodes(self, num_nodes):
        self.status_bar.children()[2].setText('Versions: {}'.format(num_nodes))

    def load_repo_file(self, file_hash):
        update_repo_index_curr_object(self.file_path, file_hash)
        self.file_hash = file_hash
        self.editor.clear()
        self.editor.text = repo_object(self.file_path, file_hash)

    # Helper functions
    def load_file(self, file_path):
        with open(file_path, 'r') as f:
            self.editor.text = f.read()

    def store_file(self, file_path):
        with open(file_path, 'w') as f:
            f.write(self.editor.text)

    def update_file_path_and_hash(self, file_path):
        self.file_path = file_path
        if self.file_path:
            self.file_hash = get_hash(self.editor.text)
        else:
            self.file_hash = None

    def index_curr_is_different_from_file_in_editor(self):
        return repo_index_curr_object(self.file_path) != get_hash(self.editor.text)

    def instantiate_index(self):
        # Instantiate new repo if needed
        if not repo_exists(self.file_path):
            init_repo(self.file_path, self.editor.text)

        # Account for outdated repos with same file path
        if self.index_curr_is_different_from_file_in_editor():
            if repo_object_exists(self.file_path, self.file_hash):
                update_repo_index_curr_object(self.file_path, self.file_hash)
            else:
                build_bridge(self.file_path, self.editor.text)

    def port_existing_repo_to_new_path(self, new_file_path):
        copy_repo(old_file_path=self.file_path, new_file_path=new_file_path)

    def new_file_built_upon_existing_one(self, new_file_path):
        return self.file_path and self.file_path != new_file_path


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ml = MaroonLines()
    sys.exit(app.exec_())
