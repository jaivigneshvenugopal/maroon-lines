from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import networkx as nx
import control

from grave import plot_network
from grave.style import use_attributes


class PrettyWidget(QWidget):

    def __init__(self):
        super(PrettyWidget, self).__init__()
        self.index = None
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('pick_event', self.pick_event)
        self.root = None
        self.curr = None
        self.root_color = 'C1'
        self.curr_color = '#32CD32'
        self.middle_color = '#add8e6'
        self.configure_layout()

    def pick_event(self, event):
        # if we did not hit a node, bail
        if not hasattr(event, 'nodes') or not event.nodes:
            return

        # pull out the graph,
        graph = event.artist.graph
        for node in event.nodes:
            graph.nodes[node]['color'] = self.curr_color
            if self.curr == self.root:
                graph.nodes[self.curr]['color'] = self.root_color
            else:
                graph.nodes[self.curr]['color'] = self.middle_color
            self.curr = node


        event.artist.stale = True
        event.artist.figure.canvas.draw_idle()

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
        graph = nx.DiGraph()
        edges = []
        nodes = []
        self.root = self.index['root']
        self.curr = self.index['current']

        for key, values in self.index.items():
            if key != 'root' and key != 'current':
                nodes.append(key)
                for val in values:
                    edges.append((key, val))

        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)
        for node, node_attrs in graph.nodes(data=True):
            if node == self.root:
                node_attrs['color'] = self.root_color
            elif node == self.curr:
                node_attrs['color'] = self.curr_color
            else:
                node_attrs['color'] = self.middle_color
            node_attrs['size'] = 200

        plot = plot_network(graph, layout="spectral", node_style=use_attributes(),
                           edge_style=use_attributes())
        plot.set_picker(10)
        self.canvas.draw_idle()

if __name__ == '__main__':
    import sys  
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create("gtk"))
    screen = PrettyWidget() 
    screen.show()   
    sys.exit(app.exec_())
