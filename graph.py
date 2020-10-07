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
        self.canvas.mpl_connect('pick_event', self.hilighter)
        self.configure_layout()

    def hilighter(self, event):
        # if we did not hit a node, bail
        if not hasattr(event, 'nodes') or not event.nodes:
            return

        # pull out the graph,
        graph = event.artist.graph

        # clear any non-default color on nodes
        for node, attributes in graph.nodes.data():
            attributes.pop('color', None)

        for u, v, attributes in graph.edges.data():
            attributes.pop('width', None)

        for node in event.nodes:
            graph.nodes[node]['color'] = 'C1'

            for edge_attribute in graph[node].values():
                edge_attribute['width'] = 3

        # update the screen
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
        root = self.index['root']
        curr = self.index['current']

        for key, values in self.index.items():
            if key != 'root' and key != 'current':
                nodes.append(key)
                for val in values:
                    edges.append((key, val))

        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)
        for node, node_attrs in graph.nodes(data=True):
            if node == root:
                node_attrs['color'] = '#fed8b1'
            elif node == curr:
                node_attrs['color'] = '#32CD32'
            else:
                node_attrs['color'] = '#add8e6'
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
