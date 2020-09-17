import sys
from PyQt5 import QtWidgets
from ui import Ui_MainWindow
from pre_ui import UI


class App:
	def __init__(self):
		app = QtWidgets.QApplication(sys.argv)
		self.ui = UI()
		self.ui.show()
		sys.exit(app.exec_())


if __name__ == "__main__":
	App()
