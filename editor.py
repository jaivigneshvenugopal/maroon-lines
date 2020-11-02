import sys
# Here, you might want to set the ``QT_API`` to use.
# Valid values are: 'pyqt5', 'pyqt4' or 'pyside'
# See
# import os; os.environ['QT_API'] = 'pyside'
from pyqode.core import api
from pyqode.core.api import CodeEdit
from pyqode.core import modes
from pyqode.core import panels
from pyqode.qt import QtWidgets

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class PyQodeEditor(CodeEdit):

    MONOKAI_THEME = 'monokai'

    def __init__(self):
        super().__init__()
        self.configure_editor()

    def configure_editor(self):
        self.configure_backend()
        self.configure_modes_and_panels()
        self.configure_font()
        self.configure_aesthetics()
        # self.file.open(__file__)

    def configure_modes_and_panels(self):
        # Modes
        self.modes.append(modes.AutoIndentMode())
        self.modes.append(modes.PygmentsSyntaxHighlighter(self.document()))

        # Panels
        line_num_area = panels.LineNumberPanel()
        line_num_area.setStyleSheet("background-color: #f0f0f0;")
        self.panels.append(line_num_area, api.Panel.Position.LEFT)
        self.panels.append(panels.SearchAndReplacePanel(), api.Panel.Position.BOTTOM)

    # Start the backend as soon as possible
    def configure_backend(self):
        self.backend.start('editor_backend.py')

    def configure_aesthetics(self):
        self.setStyleSheet("background-color: #fcfcfc")
        self.configure_scrollbar_aesthetics()

    def configure_font(self):
        self.font_name = 'Source Code Pro'
        self.font_size = 14

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
        scroll_bar.rangeChanged.connect(self.move_scroll)
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

    def move_scroll(self, _, max_val):
        self.verticalScrollBar().setSliderPosition(max_val)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    editor = PyQodeEditor()
    window.setCentralWidget(editor)
    window.showMaximized()
    app.exec_()
