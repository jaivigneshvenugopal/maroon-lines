import sys
from PyQt5 import QtWidgets
from components.maroon_lines import MaroonLines


class App:
	def __init__(self):
		app = QtWidgets.QApplication(sys.argv)
		self.ml = MaroonLines()
		self.ml.show()
		sys.exit(app.exec_())


if __name__ == "__main__":
	App()
