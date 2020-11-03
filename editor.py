import sys
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

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from pygments.lexers.python import PythonLexer
from pygments.lexers.jvm import JavaLexer, ScalaLexer
from pygments.lexers.c_cpp import CppLexer, CLexer
from pygments.lexers.javascript import JavascriptLexer
from pygments.lexers.html import HtmlLexer
from pygments.lexers.css import CssLexer
from pygments.lexers.sql import SqlLexer
from pygments.lexers.shell import BashLexer
from pygments.lexers.ruby import RubyLexer


class LineNumberPanel(DefaultLineNumberPanel):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f0f0f0;")

    def line_number_area_width(self):
        """
        Computes the lineNumber area width depending on the number of lines
        in the document

        :return: Width
        """
        digits = 2
        count = max(1, self.editor.blockCount())
        while count >= 100:
            count /= 10
            digits += 1
        space = 5 + self.editor.fontMetrics().width("9") * digits

        return space


class PyQodeEditor(CodeEdit):

    THEME = 'qt'

    def __init__(self):
        super().__init__()

        self.lexers = {
            'py': PythonLexer,
            'c': CLexer,
            'h': CLexer,
            'idc': CLexer,
            'cpp': CppLexer,
            'java': JavaLexer,
            'js': JavascriptLexer,
            'sh': BashLexer,
            'sql': SqlLexer,
            'css': CssLexer,
            'html': HtmlLexer,
            'rb': RubyLexer,
            'scala': ScalaLexer
        }

        # Instantiate Components
        self.configure_backend()
        self.configure_modes_and_panels()
        self.configure_font()
        self.configure_aesthetics()
        self.configure_actions_and_shortcuts()
        # self.file.open(__file__)

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

    def configure_modes_and_panels(self):

        # Modes
        self.modes.append(modes.IndenterMode())
        self.modes.append(modes.AutoIndentMode())
        self.modes.append(modes.AutoCompleteMode())

        # Panels
        self.panels.append(LineNumberPanel(), api.Panel.Position.LEFT)
        self.panels.append(panels.SearchAndReplacePanel(), api.Panel.Position.BOTTOM)

    def configure_syntax_highlighting(self, extension=None):
        if modes.PygmentsSyntaxHighlighter in self.modes:
            self.highlighting_syntax = True
            self.modes.remove(modes.PygmentsSyntaxHighlighter)

        if extension in self.lexers:
            lexer = self.lexers[extension]
            syntax_highlighter = modes.PygmentsSyntaxHighlighter(self.document(), lexer=lexer())
            syntax_highlighter.pygments_style = self.THEME
            self.modes.append(syntax_highlighter)

    # Start the backend as soon as possible
    def configure_backend(self):
        self.backend.start('editor_backend.py')

    def configure_aesthetics(self):
        self.setStyleSheet("background-color: #fcfcfc")
        self.configure_scrollbar_aesthetics()

    def configure_font(self):
        self.font_name = 'Source Code Pro'
        self.font_size = 12

    def set_text(self, text):
        self.setPlainText(text, 'text/plain', 'utf-8')

    def clear_text(self):
        self.setPlainText('', 'text/plain', 'utf-8')

    def get_text(self):
        return self.toPlainText()

    def get_lines(self):
        return max(1, self.blockCount())

    def configure_scrollbar_aesthetics(self):
        self.setCenterOnScroll(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        scroll_bar = self.verticalScrollBar()
        scroll_bar.rangeChanged.connect(self.ensure_cursor_is_visible)
        scroll_bar.setStyleSheet(
            """QScrollBar:vertical {
                    width: 12px;
                    margin: 0;
                    background: #fcfcfc;
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

    def ensure_cursor_is_visible(self):
        self.ensureCursorVisible()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    editor = PyQodeEditor()
    window.setCentralWidget(editor)
    window.showMaximized()
    app.exec_()
