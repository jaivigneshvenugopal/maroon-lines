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


class Editor(CodeEdit):

    MONOKAI_THEME = 'monokai'

    def __init__(self):
        super().__init__()
        self.configure_editor()

    def configure_editor(self):
        # start the backend as soon as possible
        self.backend.start('editor_backend.py')

        # append some modes and panels
        self.modes.append(modes.CodeCompletionMode())
        self.modes.append(modes.PygmentsSyntaxHighlighter(self.document()))
        self.modes.append(modes.CaretLineHighlighterMode())
        self.panels.append(panels.SearchAndReplacePanel(), api.Panel.Position.BOTTOM)

        self.modes.get(modes.PygmentsSyntaxHighlighter).pygments_style = 'dracula'
        self.file.open(__file__)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    editor = Editor()
    window.setCentralWidget(editor)
    window.showMaximized()
    app.exec_()
