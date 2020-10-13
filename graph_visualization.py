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


class GraphVisualization(QMainWindow):
    current_node = PyQt5.QtCore.pyqtSignal(str)

    def __init__(self):
        super(GraphVisualization, self).__init__()
        self.index = None
        self.figure = plt.figure()
        self.figure.set_facecolor('#fff0f0')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('pick_event', self.pick_event)
        self.root = None
        self.curr = None
        self.node_matrix = None
        self.temp_color = '#66ce62'
        self.root_color = '#006400'
        self.curr_color = '#d00000'
        self.middle_color = '#25B0B0'
        self.default_node_size = 200
        self.configure_layout()

    def pick_event(self, event):
        # if we did not hit a node, bail
        if not hasattr(event, 'nodes') or not event.nodes:
            return

        # pull out the graph,
        graph = event.artist.graph
        for node in event.nodes:
            if node == self.curr:
                return

            graph.nodes[node]['color'] = self.curr_color
            if self.curr == self.root:
                graph.nodes[self.curr]['color'] = self.root_color
            else:
                graph.nodes[self.curr]['color'] = self.middle_color
            self.curr = node

        event.artist.stale = True
        event.artist.figure.canvas.draw_idle()
        self.current_node.emit(self.curr)

    def configure_layout(self):
        self.setCentralWidget(self.canvas)
        self.show()

    def render_graph(self, index=None):
        self.index = index
        if self.index:
            eval('self.draw_graph()')
        else:
            eval('self.draw_temp_graph()')

    def draw_temp_graph(self):
        self.figure.clf()
        graph = nx.DiGraph()
        nodes = ['temp']

        graph.add_nodes_from(nodes)
        for _, node_attrs in graph.nodes(data=True):
            node_attrs['color'] = self.temp_color
            node_attrs['size'] = self.default_node_size

        plot = plot_network(graph, layout='spring', node_style=use_attributes())
        plot.set_picker(1)
        plot.axes.set_position([0.02, 0, 0.98, 1])
        self.canvas.draw_idle()

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
            elif node == self.curr:
                node_attrs['color'] = self.curr_color
            else:
                node_attrs['color'] = self.middle_color
            node_attrs['size'] = self.default_node_size

        for u, v, attrs in graph.edges.data():
            attrs['width'] = 1.5

        plot = plot_network(graph, layout=self.sequential_layout, node_style=use_attributes(), edge_style=use_attributes())
        plot.set_picker(1)
        plot.axes.set_position([0.02, 0, 0.98, 1])
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

        for key, values in self.index.items():
            pos_x, _ = self.fill_pos_x(values, pos_x[self.root], pos_x)

        seq_layout = {}
        self.node_matrix = [[None for _ in range(len(dict.fromkeys(pos_y.values())))] for _ in range(len(dict.fromkeys(pos_x.values())))]
        for i, k in enumerate(graph.nodes.keys()):
            seq_layout[k] = [pos_x[k], pos_y[k]]
            self.node_matrix[pos_x[k]][pos_y[k]] = k

        return seq_layout

    def fill_pos_x(self, values, counter, pos_x):
        for val in values:
            if val not in pos_x:
                pos_x[val] = counter
                _, counter = self.fill_pos_x(self.index[val], counter, pos_x)
        if values:
            return pos_x, counter
        else:
            return pos_x, counter + 1
