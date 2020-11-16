import sys
from PyQt5 import QtWidgets
from components.maroon_lines import MaroonLines
from fbs_runtime.application_context.PyQt5 import ApplicationContext


class App:
	def __init__(self):
		app = ApplicationContext()
		self.ml = MaroonLines()
		self.ml.show()
		sys.exit(app.app.exec_())


if __name__ == "__main__":
	App()
