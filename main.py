import sys
from PyQt5 import QtWidgets
from ui import Ui_MainWindow

class App:
	def __init__(self):
		app = QtWidgets.QApplication(sys.argv)
		self.MainWindow = QtWidgets.QMainWindow()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self.MainWindow)

		self.widget_actions()


		self.MainWindow.show()
		sys.exit(app.exec_())

	def widget_actions(self):
		self.ui.actionExit.setStatusTip('Exit Maroon Lines')
		self.ui.actionExit.triggered.connect(self.close_GUI)

	def close_GUI(self):
		self.MainWindow.close()

if __name__ == "__main__":
	App()
