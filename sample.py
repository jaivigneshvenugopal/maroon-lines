import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPlainTextEdit
# from PyQt5.Qsci import *
import qutepart


class CustomMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.__editor = qutepart.Qutepart()
        self.setCentralWidget(self.__editor)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myGUI = CustomMainWindow()
    sys.exit(app.exec_())