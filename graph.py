from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import networkx as nx
import marooncontrol

class PrettyWidget(QWidget):

    NumButtons = ['plot3']

    def __init__(self):
        super(PrettyWidget, self).__init__()        
        self.index = None
        font = QFont()
        font.setPointSize(16)
        self.initUI()

    def initUI(self):
        self.index = marooncontrol.repo_index('/home/jaivigneshvenugopal/code/maroon-lines/vig')
        self.setGeometry(100, 100, 800, 600)
        self.center()
        self.setWindowTitle('S Plot')

        grid = QGridLayout()
        self.setLayout(grid)
        self.createVerticalGroupBox()

        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(self.verticalGroupBox)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)        
        grid.addWidget(self.canvas, 0, 1, 7, 7)
        grid.addLayout(buttonLayout, 0, 0)

        self.show()


    def createVerticalGroupBox(self):
        self.verticalGroupBox = QGroupBox()

        layout = QVBoxLayout()
        i = self.NumButtons[0]
        button = QPushButton(i)
        button.setObjectName(i)
        layout.addWidget(button)
        layout.setSpacing(10)
        self.verticalGroupBox.setLayout(layout)
        button.clicked.connect(self.submitCommand)

    def submitCommand(self):
        eval('self.' + str(self.sender().objectName()) + '()')

    def plot3(self):
        self.figure.clf()
        B = nx.Graph()
        edges = []
        nodes = []
        for key, values in self.index.items():
            if key != 'root' and key != 'current':
                nodes.append(key)
                for val in values:
                    edges.append((key, val))

        B.add_nodes_from(nodes)
        B.add_edges_from(edges)
        nx.draw(B, arrows=True)
        self.canvas.draw_idle()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
    import sys  
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create("gtk"))
    screen = PrettyWidget() 
    screen.show()   
    sys.exit(app.exec_())
