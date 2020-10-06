from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import networkx as nx
import control


class PrettyWidget(QWidget):

    def __init__(self):
        super(PrettyWidget, self).__init__()
        self.index = None
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.configure_layout()

    def configure_layout(self):
        grid = QHBoxLayout()
        grid.addWidget(self.canvas)
        self.setLayout(grid)
        self.show()

    def render_graph(self, index):
        self.index = index
        eval('self.draw_graph()')

    def draw_graph(self):
        self.figure.clf()
        B = nx.DiGraph()
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


if __name__ == '__main__':
    import sys  
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create("gtk"))
    screen = PrettyWidget() 
    screen.show()   
    sys.exit(app.exec_())
