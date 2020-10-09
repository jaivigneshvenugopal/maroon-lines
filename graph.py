import PyQt5
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

from IPython import embed


class PrettyWidget(QWidget):
    current_node = PyQt5.QtCore.pyqtSignal(str)

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
        self.root_curr_node_size = 250
        self.default_node_size = 200
        self.configure_layout()

    def pick_event(self, event):
        # if we did not hit a node, bail
        if not hasattr(event, 'nodes') or not event.nodes:
            return

        # pull out the graph,
        graph = event.artist.graph
        for node in event.nodes:
            graph.nodes[node]['color'] = self.curr_color
            graph.nodes[node]['size'] = self.root_curr_node_size
            if self.curr == self.root:
                graph.nodes[self.curr]['color'] = self.root_color
                graph.nodes[self.curr]['size'] = self.root_curr_node_size
            else:
                graph.nodes[self.curr]['color'] = self.middle_color
                graph.nodes[self.curr]['size'] = self.default_node_size
            self.curr = node

        event.artist.stale = True
        event.artist.figure.canvas.draw_idle()
        self.current_node.emit(self.curr)

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
        self.index.pop('root')
        self.index.pop('current')

        for key, values in self.index.items():
            nodes.append(key)
            for val in values:
                edges.append((key, val))

        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)
        for node, node_attrs in graph.nodes(data=True):
            if node == self.root:
                node_attrs['color'] = self.root_color
                node_attrs['size'] = self.root_curr_node_size
            elif node == self.curr:
                node_attrs['color'] = self.curr_color
                node_attrs['size'] = self.root_curr_node_size
            else:
                node_attrs['color'] = self.middle_color
                node_attrs['size'] = self.default_node_size

        for u, v, attrs in graph.edges.data():
            attrs['width'] = 1.5

        plot = plot_network(graph, layout=self.sequential_layout, node_style=use_attributes(), edge_style=use_attributes())
        plot.set_picker(1)
        self.canvas.draw_idle()

    def sequential_layout(self, graph):
        pos_y = {
            self.root: 0
        }
        for key, values in self.index.items():
            for val in values:
                pos_y[val] = pos_y[key] + 1

        pos_x = {
            self.root: 0
        }
        next_count = 1
        for key, values in self.index.items():
            counter = pos_x[key]
            for val in values:
                pos_x[val] = counter
                counter = next_count
                next_count += 1
        return {k: [pos_x[k], pos_y[k]] for i, k in enumerate(graph.nodes.keys())}
