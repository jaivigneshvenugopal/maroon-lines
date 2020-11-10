import sys
from random import random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils.repository_control import *
from components.editor import PyQodeEditor
from components.timeline import Timeline
from components.unsaved_content_dialog import UnsavedContentDialog
from components.alert_dialog import AlertDialog
from components.menu_bar import MenuBar


class MaroonLines(QMainWindow):
    """
    Class responsible for stitching up the various components together - Editor, Graph etc.

    """

    DEFAULT_FILE_NAME = 'untitled'
    BACKGROUND_COLOR = '#33333d'

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value

        if self.status_bar:
            self.update_status_bar_file_path()

        # Enable rename action only when there is a repo present.
        if self.rename_move_action:
            self.rename_move_action.setEnabled(value != None)

        # Enable clear history action only when there is a repo present.
        if self.clear_history_action:
            self.clear_history_action.setEnabled(value != None)

        # Configure syntax highlighting everytime file name changes.
        if self.editor:
            extension = self.get_extension(value)
            self.editor.configure_syntax_highlighting(extension)

    @property
    def file_name(self):
        """
        Display name for file path.

        """
        return self.file_path or self.DEFAULT_FILE_NAME

    def __init__(self):
        super(QMainWindow, self).__init__()

        # Repo-related properties
        self.index = None
        self.head_node_changed = False

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

    def eventFilter(self, source, event):
        """
        Event filter for Editor to ignore certain shortcuts pertaining to Graph.

        """
        if event.type() != QEvent.KeyPress or event.modifiers() != Qt.AltModifier:
            return False

        if not self.file_path or event.key() not in self.shortcut_arrow_functions:
            return False

        if not self.content_is_saved():
            return False

        if event.isAutoRepeat():
            return True

        traverse = self.shortcut_arrow_functions[event.key()]
        traverse()

        return True

    def closeEvent(self, event):
        """
        Ensure content is saved before window is closed.

        """
        if not self.content_is_saved(close_window=True):
            event.ignore()
        else:
            event.accept()

    def configure_layout_and_central_widget(self):
        """
        Define layout and set a central widget to QMainWindow.

        """
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setStyleSheet("background-color: #f0b034")
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    def configure_menu_bar(self):
        self.setMenuBar(self.menu_bar)
        self.configure_menu_bar_actions()

    def configure_menu_bar_actions(self):
        """
        Create all relevant actions necessary for a source code editor

        """
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

        # Development code - comment out during production
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

    # Development code - comment out during production
    def handle_insert_action(self):
        self.editor.set_text(str(random()))
        self.handle_save_action()

    def configure_status_bar(self):
        """
        Display 4 crucial information through the use of status bar

        1. Number of lines
        2. Language used
        3. File path of current file in session
        4. Number of versions for current file in session

        """
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: #33333d;
                color: #CDD7D3;
                font: 17px;
            }
        """)

        self.status_bar_num_lines_label.setAlignment(Qt.AlignLeft)
        self.status_bar_num_lines_label.setStyleSheet("""
            QLabel {
                color: #CDD7D3;
                padding-left: 2px;
            }
        """)

        self.status_bar_num_nodes_label.setAlignment(Qt.AlignRight)
        self.status_bar_num_nodes_label.setStyleSheet("""
            QLabel {
                color: #CDD7D3;
                padding-right: 2px;
            }
        """)

        self.status_bar_file_path_label.setAlignment(Qt.AlignCenter)
        self.status_bar_file_path_label.setStyleSheet("""
            QLabel {
                color: #CDD7D3;
            }
        """)

        self.status_bar_curr_language_label.setText(self.editor.DEFAULT_LANGUAGE)
        self.status_bar_curr_language_label.setAlignment(Qt.AlignLeft)
        self.status_bar_curr_language_label.setStyleSheet("""
            QLabel {
                color: #CDD7D3;
                padding-right: 2px;
            }
        """)

        self.status_bar.addPermanentWidget(self.status_bar_num_lines_label, 10)
        self.status_bar.addPermanentWidget(self.status_bar_curr_language_label, 30)
        self.status_bar.addPermanentWidget(self.status_bar_file_path_label, 120)
        self.status_bar.addPermanentWidget(self.status_bar_num_nodes_label, 40)

        self.update_status_bar_file_path()
        self.update_status_bar_num_lines()

    def configure_graph(self):
        self.graph.request_to_change_node.connect(self.handle_request_to_change_node)
        self.graph.head_node_changed.connect(self.load_repo_file_object)
        self.graph.num_nodes_changed.connect(self.update_status_bar_num_nodes)
        self.graph.render_graph(index=None)
        self.layout.addWidget(self.graph, 15)

    def configure_and_show_frame(self):
        """
        Define the geometry of the application and show it.

        """
        self.setGeometry(500, 250, 1000, 500)
        self.setWindowTitle("Maroon Lines")
        self.showMaximized()

    def handle_new_action(self):
        """
        Clean editor, graph and all relevant components to start afresh.

        """
        if not self.content_is_saved():
            return

        self.editor.clear_text()
        self.editor.clear_modified_flag()

        self.update_file_path_and_hash()

        self.graph.render_graph(index=None)

    def handle_open_action(self):
        """
        Load a new file and kickstart relevant component changes.

        """
        if not self.content_is_saved():
            return

        file_info = QFileDialog.getOpenFileName(self, 'Open File')
        file_path, file_type = str(file_info[0]), file_info[1]

        if not file_path:
            return

        self.editor.load_file(file_path)
        self.editor.clear_modified_flag()

        self.update_file_path_and_hash(file_path)
        self.update_index()

        self.graph.render_graph(repo_index(self.file_path))

    def handle_save_action(self):
        """
        Save file in session and update repo.

        :return: Boolean representing result of handling the action

        """
        if not self.file_path:
            return self.handle_save_as_action()

        self.editor.store_file(self.file_path)
        self.editor.clear_modified_flag()

        file_data = self.editor.get_text()
        self.file_hash = get_hash(file_data)

        if repo_file_object_exists(self.file_path, self.file_hash):
            update_repo_index_head(self.file_path, self.file_hash)
        else:
            add_file_object_to_index(self.file_path, file_data)

        self.graph.render_graph(repo_index(self.file_path))

        return True

    def handle_save_as_action(self):
        """
        Save file in session and create new repo.

        :return: Boolean representing result of handling the action
        """
        file_info = QFileDialog.getSaveFileName(self, 'Save As...')
        file_path, file_type = str(file_info[0]), file_info[1]

        if not file_path:
            return False

        # if save_as function is actually a save function in disguise
        if self.file_path and self.file_path == file_path:
            return self.handle_save_action()

        # if there is an intent to create a copy of the file and its history
        if self.file_path and self.file_path != file_path:
            copy_repo(old_file_path=self.file_path, new_file_path=file_path)

        self.editor.store_file(file_path)
        self.editor.clear_modified_flag()

        self.update_file_path_and_hash(file_path)
        self.update_index()

        self.graph.render_graph(repo_index(self.file_path))

        return True

    def handle_rename_move_action(self):
        if not self.file_path:
            return

        file_info = QFileDialog.getSaveFileName(self, 'Move/Rename')
        file_path, file_type = str(file_info[0]), file_info[1]

        if not file_path or self.file_path == file_path:
            return

        self.editor.store_file(file_path)
        self.move_file(file_path)
        self.update_file_path_and_hash(file_path)
        self.update_index()
        self.editor.document().setModified(False)
        self.graph.render_graph(repo_index(self.file_path))

    def handle_exit_action(self):
        self.close()

    def handle_clear_history_action(self):
        dialog = AlertDialog(self.file_path, text_to_display='Are you sure about clearing your file history?')
        clicked_button = dialog.exec_()

        if not clicked_button or clicked_button == QDialogButtonBox.Cancel:
            return

        if self.index_curr_is_different_from_file_in_editor():
            rebuilt_repo(self.file_path, repo_file_object(self.file_path, self.file_hash))
            self.graph.render_graph(self.add_unsaved_node())
            self.editor.document().setModified(True)
        else:
            rebuilt_repo(self.file_path, self.editor.get_text())
            self.graph.render_graph(repo_index(self.file_path))
            self.editor.document().setModified(False)

    # Instantiate editor
    def configure_editor(self):
        self.editor.language.connect(self.update_status_bar_language)
        self.editor.textChanged.connect(self.update_status_bar_num_lines)
        self.editor.modificationChanged.connect(self.display_graph_in_edit_mode)
        self.editor.installEventFilter(self)
        self.layout.addWidget(self.editor, 85)

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
        if not self.content_is_saved():
            return

        self.graph.switch_node_colors(node)

    def display_graph_in_edit_mode(self, changed):
        if not changed:
            return

        if not self.file_path or not self.file_hash:
            return

        if self.head_node_changed:
            self.head_node_changed = False
            return

        self.editor.document().setModified(True)
        self.graph.render_graph(self.add_unsaved_node())

    def add_unsaved_node(self):
        index = repo_index(self.file_path)
        curr = index['head']
        index[curr].append('unsaved_node')
        index['unsaved_node'] = []

        return index

    def load_repo_file_object(self, file_hash):
        update_repo_index_head(self.file_path, file_hash)
        self.file_hash = file_hash
        self.head_node_changed = True
        self.editor.set_text(repo_file_object(self.file_path, file_hash))
        self.editor.store_file(self.file_path)

        if self.editor.document().isModified():
            self.graph.render_graph(repo_index(self.file_path))
            self.editor.document().setModified(False)

    # Helper functions
    def update_file_path_and_hash(self, file_path=None):
        self.file_path = file_path
        if self.file_path:
            self.file_hash = get_hash(self.editor.get_text())
        else:
            self.file_hash = None

    def index_curr_is_different_from_file_in_editor(self):
        return repo_index_head(self.file_path) != get_hash(self.editor.get_text())

    def file_content_changed(self):
        return self.file_hash != get_hash(self.editor.get_text())

    def update_index(self):
        if not repo_exists(self.file_path):
            init_repo(self.file_path, self.editor.get_text())

        if self.index_curr_is_different_from_file_in_editor():
            if repo_file_object_exists(self.file_path, self.file_hash):
                update_repo_index_head(self.file_path, self.file_hash)
            else:
                add_file_object_to_index(self.file_path, self.editor.get_text(), adopted=True)

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

    def content_is_saved(self, close_window=False):
        if (not self.file_path and not self.editor.get_text()) or \
                (self.file_path and self.file_hash == get_hash(self.editor.get_text())):
            return True

        dialog = UnsavedContentDialog(self.file_name,
                                      text_to_display='Do you want to save your changes?',
                                      close_window=close_window)
        clicked_button = dialog.exec_()

        if not clicked_button or clicked_button == QDialogButtonBox.Cancel:
            return False
        elif clicked_button == QDialogButtonBox.Save:
            return self.handle_save_action()
        elif clicked_button == QDialogButtonBox.Ignore or clicked_button == QDialogButtonBox.Close:
            return True

    @staticmethod
    def get_extension(value):
        """
        :param value: file_path
        :return: extension of file_path
        """
        if value:
            _, ext = os.path.splitext(value)
            return ext
        else:
            return None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ml = MaroonLines()
    sys.exit(app.exec_())
