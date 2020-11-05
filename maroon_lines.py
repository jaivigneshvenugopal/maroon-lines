import sys
from random import random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from editor import PyQodeEditor
from repository_control_utils import *
from timeline import Timeline
from dialog import Dialog
from menu_bar import MenuBar
from IPython import embed


class MaroonLines(QMainWindow):
    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value

        if self.status_bar:
            self.update_status_bar_file_path()

        if self.rename_move_action:
            self.rename_move_action.setEnabled(value != None)

        if self.clear_history_action:
            self.clear_history_action.setEnabled(value != None)

        if self.editor:
            extension = value.split('.')[-1] if value else None
            self.editor.configure_syntax_highlighting(extension)

    @property
    def file_name(self):
        return self.file_path or 'untitled'

    def __init__(self):
        super(QMainWindow, self).__init__()

        # Repo-related properties
        self.index = None
        self.curr_node_changed = False

        # Widget-related properties
        self.layout = QHBoxLayout()
        self.central_widget = QWidget()
        self.menu_bar = MenuBar()
        self.editor = PyQodeEditor()
        self.graph = Timeline()
        self.status_bar = QStatusBar()
        self.status_bar_num_lines_label = QLabel()
        self.status_bar_num_nodes_label = QLabel()
        self.status_bar_file_path_label = QLabel()
        self.status_bar_curr_language_label = QLabel()

        # Menu bar related properties
        self.rename_move_action = None
        self.clear_history_action = None

        # File-related properties
        self.file_path = None
        self.file_hash = None
        self.file_is_already_in_edit_mode = False

        # Editor-related properties
        self.syntax_highlighting = False

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
        if event.type() != QEvent.KeyPress or event.modifiers() != Qt.AltModifier:
            return False

        if not self.file_path or event.key() not in self.shortcut_arrow_functions:
            return False

        if not self.content_is_saved(window_close=False):
            return False

        if event.isAutoRepeat():
            return True

        traverse = self.shortcut_arrow_functions[event.key()]
        traverse()

        return True

    def closeEvent(self, event):
        if not self.content_is_saved(window_close=True):
            event.ignore()
        else:
            event.accept()

    # Define layout and set a central widget to QMainWindow
    def configure_layout_and_central_widget(self):
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setStyleSheet("background-color: #f0b034")
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    # Refactored
    def configure_menu_bar(self):
        self.setMenuBar(self.menu_bar)
        self.configure_menu_bar_actions()

    def configure_menu_bar_actions(self):
        file_menu = self.menu_bar.addMenu('File')
        repo_menu = self.menu_bar.addMenu('Repo')

        new_action = file_menu.addAction('New')
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.handle_new_action)

        open_action = file_menu.addAction('Open')
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.handle_open_action)

        save_action = file_menu.addAction('Save')
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.handle_save_action)

        save_as_action = file_menu.addAction('Save As...')
        save_as_action.setShortcut("Shift+Ctrl+S")
        save_as_action.triggered.connect(self.handle_save_as_action)

        exit_action = file_menu.addAction('Exit')
        exit_action.setShortcut("Ctrl+W")
        exit_action.triggered.connect(self.handle_exit_action)

        # Development code - delete during production
        insert_test_text = file_menu.addAction('Insert Random Text and Save File')
        insert_test_text.setShortcut("Ctrl+L")
        insert_test_text.triggered.connect(self.handle_insert_action)

        self.rename_move_action = repo_menu.addAction('Move/Rename')
        self.rename_move_action.setShortcut("Ctrl+M")
        self.rename_move_action.triggered.connect(self.handle_rename_move_action)
        self.rename_move_action.setEnabled(False)

        self.clear_history_action = repo_menu.addAction('Clear History')
        self.clear_history_action.triggered.connect(self.handle_clear_history_action)
        self.clear_history_action.setEnabled(False)

    # Development code - delete during production
    def handle_insert_action(self):
        self.editor.set_text(str(random()))
        self.handle_save_action()

    # Refactored
    def configure_status_bar(self):
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: rgb(51, 51, 61);
                color: rgb(205,215,211);
                font: 17px;
            }
        """)

        self.status_bar_num_lines_label.setAlignment(Qt.AlignLeft)
        self.status_bar_num_lines_label.setStyleSheet("""
            QLabel {
                color: rgb(205,215,211);
                padding-left: 2px;
            }
        """)

        self.status_bar_num_nodes_label.setAlignment(Qt.AlignRight)
        self.status_bar_num_nodes_label.setStyleSheet("""
            QLabel {
                color: rgb(205,215,211);
                padding-right: 2px;
            }
        """)

        self.status_bar_file_path_label.setAlignment(Qt.AlignCenter)
        self.status_bar_file_path_label.setStyleSheet("""
            QLabel {
                color: rgb(205,215,211);
            }
        """)

        self.status_bar_curr_language_label.setText('Text')
        self.status_bar_curr_language_label.setAlignment(Qt.AlignLeft)
        self.status_bar_curr_language_label.setStyleSheet("""
            QLabel {
                color: rgb(205,215,211);
                padding-right: 2px;
            }
        """)

        self.status_bar.addPermanentWidget(self.status_bar_num_lines_label, 10)
        self.status_bar.addPermanentWidget(self.status_bar_curr_language_label, 30)
        self.status_bar.addPermanentWidget(self.status_bar_file_path_label, 120)
        self.status_bar.addPermanentWidget(self.status_bar_num_nodes_label, 40)

        self.update_status_bar_file_path()
        self.update_status_bar_num_lines()

    # Refactored
    def configure_graph(self):
        self.graph.request_to_change_node.connect(self.handle_request_to_change_node)
        self.graph.curr_node_changed.connect(self.load_repo_file)
        self.graph.num_nodes_changed.connect(self.update_status_bar_num_nodes)
        self.layout.addWidget(self.graph, 15)
        self.graph.render_graph(index=None)

    # Define the geometry of the application and show it
    def configure_and_show_frame(self):
        self.setGeometry(500, 250, 1000, 500)
        self.setWindowTitle("Maroon Lines")
        self.showMaximized()

    # Refactored
    def handle_new_action(self):
        if not self.content_is_saved(window_close=False):
            return

        self.update_file_path_and_hash(file_path=None)
        self.editor.clear_text()
        self.file_is_already_in_edit_mode = False
        self.graph.render_graph(index=None)

    # Refactored
    def handle_open_action(self):
        if not self.content_is_saved(window_close=False):
            return

        file_info = QFileDialog.getOpenFileName(self, 'Open File')
        file_path, file_type = str(file_info[0]), file_info[1]
        if file_path:
            self.load_file(file_path)
            self.update_file_path_and_hash(file_path)
            self.update_index()
            self.file_is_already_in_edit_mode = False
            self.graph.render_graph(repo_index(self.file_path))

    # Refactored
    def handle_save_action(self):
        if not self.file_path:
            return self.handle_save_as_action()
        else:
            file_hash = get_hash(self.editor.get_text())
            if repo_object_exists(self.file_path, file_hash):
                update_repo_index_curr_object(self.file_path, file_hash)
            else:
                append_repo_object(self.file_path, file_data=self.editor.get_text(), parent_file_hash=self.file_hash)
                self.store_file(self.file_path)

            self.file_hash = file_hash
            self.file_is_already_in_edit_mode = False
            self.graph.render_graph(repo_index(self.file_path))
            return True

    # Refactored
    def handle_save_as_action(self):
        file_info = QFileDialog.getSaveFileName(self, 'Save As...')
        file_path, file_type = str(file_info[0]), file_info[1]
        if not file_path:
            return False

        if self.file_path and self.file_path == file_path:
            return self.handle_save_action()

        if self.file_path and self.file_path != file_path:
            copy_repo(old_file_path=self.file_path, new_file_path=file_path)

        self.store_file(file_path)
        self.update_file_path_and_hash(file_path)
        self.update_index()
        self.file_is_already_in_edit_mode = False
        self.graph.render_graph(repo_index(self.file_path))
        return True

    def handle_rename_move_action(self):
        if not self.file_path:
            return

        file_info = QFileDialog.getSaveFileName(self, 'Move/Rename')
        file_path, file_type = str(file_info[0]), file_info[1]

        if not file_path or self.file_path == file_path:
            return

        self.store_file(file_path)
        self.move_file(file_path)
        self.update_file_path_and_hash(file_path)
        self.update_index()
        self.file_is_already_in_edit_mode = False
        self.graph.render_graph(repo_index(self.file_path))

    # Refactored
    def handle_exit_action(self):
        self.close()

    def handle_clear_history_action(self):
        if not self.content_is_saved(window_close=False):
            return

        rebuilt_repo(self.file_path, self.editor.get_text())
        self.update_index()
        self.graph.render_graph(repo_index(self.file_path))

    # Instantiate editor
    def configure_editor(self):
        self.editor.language.connect(self.update_status_bar_language)
        self.editor.syntax_highlighting.connect(self.set_syntax_highlighting_flag)
        self.editor.textChanged.connect(self.update_relevant_components)
        self.editor.installEventFilter(self)
        self.layout.addWidget(self.editor, 85)

    def set_syntax_highlighting_flag(self):
        self.syntax_highlighting = True

    # Slot Functions
    def update_relevant_components(self):
        self.update_status_bar_num_lines()
        self.display_graph_in_edit_mode()

    def update_status_bar_num_lines(self):
        self.status_bar_num_lines_label.setText('Lines: {}'.format(self.editor.get_lines())) 

    def update_status_bar_num_nodes(self, num_nodes):
        self.status_bar_num_nodes_label.setText('Versions: {}'.format(num_nodes))

    def update_status_bar_file_path(self):
        self.status_bar_file_path_label.setText(self.file_name)

    def update_status_bar_language(self, language):
        self.status_bar_curr_language_label.setText(language)

    def handle_request_to_change_node(self, node):
        if not self.content_is_saved(window_close=False):
            return

        self.graph.switch_node_colors(node)

    def display_graph_in_edit_mode(self):
        if not self.file_path or not self.file_hash or self.file_is_already_in_edit_mode:
            return

        if self.curr_node_changed:
            self.curr_node_changed = False
            return

        if self.syntax_highlighting:
            self.syntax_highlighting = False
            return

        self.graph.render_graph(self.add_unsaved_node())
        self.file_is_already_in_edit_mode = True

    def add_unsaved_node(self):
        index = repo_index(self.file_path)
        curr = index['curr']
        index[curr].append('unsaved_node')
        index['unsaved_node'] = []

        return index

    def load_repo_file(self, file_hash):
        update_repo_index_curr_object(self.file_path, file_hash)
        self.file_hash = file_hash
        self.curr_node_changed = True
        self.editor.set_text(repo_object(self.file_path, file_hash))
        self.store_file(self.file_path)
        if self.file_is_already_in_edit_mode:
            self.graph.render_graph(repo_index(self.file_path))
            self.file_is_already_in_edit_mode = False

    # Helper functions
    def load_file(self, file_path):
        with open(file_path, 'r') as f:
            self.editor.set_text(f.read())

    def store_file(self, file_path):
        with open(file_path, 'w') as f:
            f.write(self.editor.get_text())

    def update_file_path_and_hash(self, file_path):
        self.file_path = file_path
        if self.file_path:
            self.file_hash = get_hash(self.editor.get_text())
        else:
            self.file_hash = None

    def index_curr_is_different_from_file_in_editor(self):
        return repo_index_curr_object(self.file_path) != get_hash(self.editor.get_text())

    def file_content_changed(self):
        return self.file_hash != get_hash(self.editor.get_text())

    def update_index(self):
        if not repo_exists(self.file_path):
            init_repo(self.file_path, self.editor.get_text())

        if self.index_curr_is_different_from_file_in_editor():
            if repo_object_exists(self.file_path, self.file_hash):
                update_repo_index_curr_object(self.file_path, self.file_hash)
            else:
                build_bridge(self.file_path, self.editor.get_text())

    def move_file(self, file_path):
        copy_repo(old_file_path=self.file_path, new_file_path=file_path)
        self.remove_existing_copy_of_file_and_repo()

    def remove_existing_copy_of_file_and_repo(self):
        self.remove_file(self.file_path)
        remove_repo(self.file_path)

    def remove_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise Exception('File does not exist to move/rename')

    def content_is_saved(self, window_close):
        if (not self.file_path and not self.editor.get_text()) or \
                (self.file_path and self.file_hash == get_hash(self.editor.get_text())):
            return True

        dialog = Dialog(self.file_name, window_close)
        clicked_button = dialog.exec_()

        if not clicked_button or clicked_button == QDialogButtonBox.Cancel:
            return False
        elif clicked_button == QDialogButtonBox.Save:
            return self.handle_save_action()
        elif clicked_button == QDialogButtonBox.Ignore or clicked_button == QDialogButtonBox.Close:
            return True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ml = MaroonLines()
    sys.exit(app.exec_())
