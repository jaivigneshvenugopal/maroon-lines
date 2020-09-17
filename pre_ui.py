import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        self.configure_frame()
        self.configure_editor()
        self.show()

    # Define the geometry of the main window
    def configure_frame(self):
        self.setGeometry(500, 250, 1000, 500)
        self.setWindowTitle("Maroon Lines")

    # Instantiate editor
    def configure_editor(self):
        self.__editor = QsciScintilla()
        self.__editor.setUtf8(True)  # Set encoding to UTF-8

        self.configure_indentations()
        self.configure_margins()
        self.configure_lexers()
        self.setCentralWidget(self.__editor)

    # Set indentation configurations
    def configure_indentations(self):
        self.__editor.setIndentationsUseTabs(True)
        self.__editor.setTabWidth(4)
        self.__editor.setIndentationGuides(True)
        self.__editor.setAutoIndent(True)

    # Set margin to number and set length of margin
    def configure_margins(self):
        self.__editor.setMarginWidth(0, "000")
        self.__editor.setMarginType(0, self.__editor.NumberMargin)

    # Set Lexer
    def configure_lexers(self):
        self.__lexer = QsciLexerPython(self.__editor)
        self.__editor.setLexer(self.__lexer)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = UI()
    sys.exit(app.exec_())
