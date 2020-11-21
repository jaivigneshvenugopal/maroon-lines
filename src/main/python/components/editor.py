import sys
import os
# Here, you might want to set the ``QT_API`` to use.
# Valid values are: 'pyqt5', 'pyqt4' or 'pyside'
# See
# import os; os.environ['QT_API'] = 'pyside'
from pyqode.core import api
from pyqode.core.api import CodeEdit
from pyqode.core import modes
from pyqode.core import panels
from pyqode.core.panels import LineNumberPanel as DefaultLineNumberPanel
from pyqode.qt import QtWidgets
from pyqode.python.modes import CommentsMode

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import pygments.lexers as lexers
from pygments.lexers import find_lexer_class, find_lexer_class_for_filename


class LineNumberPanel(DefaultLineNumberPanel):
    """
    Inheriting from LineNumberPanel located in pyqode.

    This class differs from its parent in the aspect of style and width of the panel.
    """
    BACKGROUND_COLOR = '#f0f0f0'

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: {};".format(self.BACKGROUND_COLOR))

    def line_number_area_width(self):
        """
        Computes the lineNumber area width depending on the number of lines
        in the document

        :return: width of line number area
        """
        digits = 2
        count = max(1, self.editor.blockCount())
        while count >= 100:
            count /= 10
            digits += 1
        width = 5 + self.editor.fontMetrics().width("9") * digits

        return width


class PyQodeEditor(CodeEdit):

    language = pyqtSignal(str)

    THEME = 'qt'
    DEFAULT_LANGUAGE = 'Text'
    BACKGROUND_COLOR = '#fcfcfc'

    FONT_NAME = 'Source Code Pro'
    FONT_SIZE = 14

    MIME = 'text/plain'
    ENCODING = 'utf-8'

    def __init__(self):
        super().__init__()

        self.highlighter = None

        # Instantiate Components
        # self.configure_backend()
        self.configure_modes_and_panels()
        self.configure_font()
        self.configure_aesthetics()
        self.configure_actions_and_shortcuts()
        # self.file.open(__file__)

    # Start the backend as soon as possible
    def configure_backend(self):
        self.backend.start('backend.py')

    def configure_modes_and_panels(self):

        # Modes
        self.modes.append(modes.IndenterMode())
        self.modes.append(modes.AutoIndentMode())
        self.modes.append(modes.AutoCompleteMode())
        self.modes.append(CommentsMode())

        # Panels
        self.panels.append(LineNumberPanel(), api.Panel.Position.LEFT)
        self.panels.append(panels.SearchAndReplacePanel(), api.Panel.Position.BOTTOM)

    def configure_font(self):
        self.font_name = self.FONT_NAME
        self.font_size = self.FONT_SIZE

    def configure_aesthetics(self):
        self.setStyleSheet("background-color: {}; border: 0px;".format(self.BACKGROUND_COLOR))
        self.configure_scrollbar_aesthetics()

    def configure_actions_and_shortcuts(self):
        self.action_swap_line_up.setShortcut('Ctrl+Shift+Up')
        self.action_swap_line_down.setShortcut('Ctrl+Shift+Down')

        # Zoom in
        zoom_in = QAction('Zoom In', self)
        zoom_in.setShortcut('Ctrl+=')
        zoom_in.triggered.connect(self.zoom_in)
        self.add_action(zoom_in, sub_menu=None)

        # Zoom out
        zoom_in = QAction('Zoom Out', self)
        zoom_in.setShortcut('Ctrl+-')
        zoom_in.triggered.connect(self.zoom_out)
        self.add_action(zoom_in, sub_menu=None)

    def configure_scrollbar_aesthetics(self):
        self.setCenterOnScroll(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        scroll_bar = self.verticalScrollBar()
        scroll_bar.rangeChanged.connect(self.ensureCursorVisible)
        scroll_bar.setStyleSheet(
            """QScrollBar:vertical {
                    width: 12px;
                    margin: 0;
                    background: #f0f0f0;
                  }

                  QScrollBar::handle:vertical {
                    border: 12px solid #d9d9d9;
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

        scroll_bar = self.horizontalScrollBar()
        scroll_bar.setStyleSheet(
            """QScrollBar:horizontal {
                    height: 12px;
                    margin: 0;
                    background: #fcfcfc;
                  }

                  QScrollBar::handle:horizontal {
                    border: 12px solid #d9d9d9;
                    background: #33333d;
                    min-width: 10px;
                  }

                  QScrollBar::add-line:horizontal {
                    width: 0px;
                  }

                  QScrollBar::sub-line:horizontal {
                    width: 0px;
                  }

                  QScrollBar::up-arrow:horizontal {
                    border: none;
                    height: 0px;
                    width: 0px;
                    background: none;
                    color: none;
                  }

                  QScrollBar::down-arrow:horizontal {
                    border: none;
                    height: 0px;
                    width: 0px;
                    background: none;
                    color: none;
                  }

                  QScrollBar::add-page:horizontal {
                    width: 0px;
                  }

                  QScrollBar::sub-page:horizontal {
                    width: 0px;
                  }""")

    def configure_syntax_highlighting(self, extension=None):
        if self.highlighter:
            self.language.emit(self.DEFAULT_LANGUAGE)
            self.highlighter = None

            # Removing the highlighter does not refresh current text
            # Therefore, it is a necessity to call the set_text method
            self.modes.remove(modes.PygmentsSyntaxHighlighter)
            self.set_text(self.get_text())

        if extension:
            lexer = find_lexer_class_for_filename(extension)
            if not lexer:
                return

            self.language.emit(lexer().name)
            self.highlighter = modes.PygmentsSyntaxHighlighter(self.document(), lexer=lexer())
            self.highlighter.pygments_style = self.THEME
            self.modes.append(self.highlighter)

    def set_text(self, text):
        self.setPlainText(text, self.MIME, self.ENCODING)
        self.clear_modified_flag()

    def clear_text(self):
        self.setPlainText('', self.MIME, self.ENCODING)
        self.clear_modified_flag()

    def get_text(self):
        return self.toPlainText()

    def load_file(self, file_path):
        with open(file_path, 'r') as f:
            self.set_text(f.read())

    def store_file(self, file_path):
        with open(file_path, 'w') as f:
            f.write(self.get_text())

        self.clear_modified_flag()

    def get_lines(self):
        return max(1, self.blockCount())

    def clear_modified_flag(self):
        self.document().setModified(False)

    def set_modified_flag(self):
        self.document().setModified(True)

    @staticmethod
    def remove_file(file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise Exception('File does not exist to move/rename')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    editor = PyQodeEditor()
    window.setCentralWidget(editor)
    window.showMaximized()
    app.exec_()
