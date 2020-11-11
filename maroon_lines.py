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
        self.timeline = Timeline()
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
            Qt.Key_Up: self.timeline.move_up,
            Qt.Key_Down: self.timeline.move_down,
            Qt.Key_Right: self.timeline.move_right,
            Qt.Key_Left: self.timeline.move_left
        }

        # Instantiate relevant components
        self.configure_layout_and_central_widget()
        self.configure_menu_bar()
        self.configure_status_bar()
        self.configure_editor()
        self.configure_timeline()
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

        self.status_bar_num_lines_label.setText('Lines: 1')
        self.status_bar_num_lines_label.setAlignment(Qt.AlignLeft)
        self.status_bar_num_lines_label.setStyleSheet("""
            QLabel {
                color: #CDD7D3;
                padding-left: 2px;
            }
        """)

        self.status_bar_num_nodes_label.setText('Versions: 1')
        self.status_bar_num_nodes_label.setAlignment(Qt.AlignRight)
        self.status_bar_num_nodes_label.setStyleSheet("""
            QLabel {
                color: #CDD7D3;
                padding-right: 2px;
            }
        """)

        self.status_bar_file_path_label.setText(self.file_name)
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

    def configure_editor(self):
        """
        Monitor 3 crucial information
        1. Language used
        2. Text Changes
        3. File modified signal after it was saved/opened/moved etc

        """
        self.editor.language.connect(self.update_status_bar_language)
        self.editor.textChanged.connect(self.update_status_bar_num_lines)
        self.editor.modificationChanged.connect(self.display_graph_in_edit_mode)
        self.editor.installEventFilter(self)
        self.layout.addWidget(self.editor, 85)

    def configure_timeline(self):
        self.timeline.request_to_change_node.connect(self.handle_request_to_change_node)
        self.timeline.head_node_changed.connect(self.load_repo_file_object)
        self.timeline.num_nodes_changed.connect(self.update_status_bar_num_nodes)
        self.render_timeline()
        self.layout.addWidget(self.timeline, 15)

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
        self.render_timeline()

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

        self.load_index(file_path)

        self.update_file_path_and_hash(file_path)
        self.render_timeline()

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

        self.render_timeline()

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

        self.editor.store_file(file_path)
        self.editor.clear_modified_flag()

        # if there is an intent to create a copy of the file and its history
        if self.file_path and self.file_path != file_path:
            copy_repo(old_file_path=self.file_path, new_file_path=file_path)
            if self.index_head_differs_from_live_text():
                # Check if newly saved content is pre-existing in repo history.
                if repo_file_object_exists(self.file_path, self.file_hash):
                    update_repo_index_head(self.file_path, self.file_hash)
                else:
                    add_file_object_to_index(self.file_path, self.editor.get_text(), adopted=True)

        # brand new file - maiden save
        if not self.file_path:
            self.create_index(file_path)

        self.update_file_path_and_hash(file_path)
        self.render_timeline()

        return True

    def handle_rename_move_action(self):
        """
        Move a file and its history to another location.

        """
        if not self.content_is_saved():
            return

        file_info = QFileDialog.getSaveFileName(self, 'Move/Rename')
        file_path, file_type = str(file_info[0]), file_info[1]

        if not file_path or self.file_path == file_path:
            return

        self.editor.remove_file(self.file_path)
        self.editor.store_file(file_path)
        self.editor.clear_modified_flag()

        move_repo(old_file_path=self.file_path, new_file_path=file_path)

        self.update_file_path_and_hash(file_path)
        self.render_timeline()

    def handle_exit_action(self):
        self.close()

    def handle_clear_history_action(self):
        """
        Remove history of a particular file and re-create a new one.

        """
        dialog = AlertDialog(self.file_path, text_to_display='Are you sure about clearing your file history?')
        clicked_button = dialog.exec_()

        if not clicked_button or clicked_button == QDialogButtonBox.Cancel:
            return

        # There will be a case where uses wishes to clear history while the current text is not saved.
        # This accounts for that case - ensuring current text is not saved but its history is cleared.
        if self.index_head_differs_from_live_text():
            file_data = repo_file_object(self.file_path, self.file_hash)
            rebuilt_repo(self.file_path, file_data)
            self.editor.set_modified_flag()
            self.render_timeline(edit_mode=True)
        else:
            file_data = self.editor.get_text()
            rebuilt_repo(self.file_path, file_data)
            self.editor.clear_modified_flag()
            self.render_timeline()

    def render_timeline(self, edit_mode=False):
        """
        Draw network.

        """
        if self.file_path:
            index = repo_index(self.file_path)
        else:
            index = None

        if index and edit_mode:
            head = index[INDEX_HEAD]
            index[head].append(self.timeline.UNSAVED_NODE)
            index[self.timeline.UNSAVED_NODE] = []

        self.timeline.render_graph(index)

    def content_is_saved(self, close_window=False):
        """
        Opens up a dialog to ask if content needs to be saved.

        :param close_window: if app is to be closed

        """
        if self.file_is_virgin() or self.file_content_did_not_change():
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

    def create_index(self, file_path):
        if repo_exists(file_path):
            remove_repo(file_path)

        init_repo(file_path, self.editor.get_text())

    def load_index(self, file_path):
        file_data = self.editor.get_text()
        if not repo_exists(file_path):
            init_repo(file_path, file_data)
            return

        if self.index_head_differs_from_live_text():
            # Check if content is pre-existing in repo history.
            if repo_file_object_exists(file_path, file_data):
                update_repo_index_head(file_path, file_data)
            else:
                # This means file was somehow edited by 3rd party, which forces the current history to adopt it.
                add_file_object_to_index(file_path, file_data, adopted=True)

    # Slot Function
    def update_status_bar_num_lines(self):
        self.status_bar_num_lines_label.setText('Lines: {}'.format(self.editor.get_lines()))

    # Slot Function
    def update_status_bar_num_nodes(self, num_nodes):
        self.status_bar_num_nodes_label.setText('Versions: {}'.format(num_nodes))

    # Slot Function
    def update_status_bar_file_path(self):
        self.status_bar_file_path_label.setText(self.file_name)

    # Slot Function
    def update_status_bar_language(self, language):
        self.status_bar_curr_language_label.setText(language)

    # Slot Function
    def handle_request_to_change_node(self, node_to_change_to):
        if not self.content_is_saved():
            return

        self.timeline.switch_node_colors(node_to_change_to)

    # Slot Function
    def display_graph_in_edit_mode(self, file_modified):
        """
        Display a unorthodox node with a dotted edge to its parent, to demonstrate the unsaved nature of a file.

        """
        if not file_modified:
            return

        if not self.file_path or not self.file_hash:
            return

        if self.head_node_changed:
            self.head_node_changed = False
            return

        self.editor.set_modified_flag()
        self.render_timeline(edit_mode=True)

    # Slot Function
    def load_repo_file_object(self, file_hash):
        self.file_hash = file_hash
        self.editor.set_text(repo_file_object(self.file_path, file_hash))
        self.editor.store_file(self.file_path)

        self.head_node_changed = True
        update_repo_index_head(self.file_path, file_hash)

        # This is to clear away the node with the dotted edge - which is displayed when file is in edit mode
        if self.file_in_edit_mode():
            self.editor.clear_modified_flag()
            self.render_timeline()

    # Helper function
    def update_file_path_and_hash(self, file_path=None):
        self.file_path = file_path
        if self.file_path:
            self.file_hash = get_hash(self.editor.get_text())
        else:
            self.file_hash = None

    # Helper function
    def index_head_differs_from_live_text(self):
        return repo_index_head(self.file_path) != get_hash(self.editor.get_text())

    # Helper function
    def file_content_did_not_change(self):
        return self.file_path and not self.index_head_differs_from_live_text()

    # Helper function
    def file_is_virgin(self):
        return not self.file_path and not self.editor.get_text()

    # Helper function
    def file_in_edit_mode(self):
        return self.editor.document().isModified()

    # Helper function
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
