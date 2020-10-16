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
        self.graph = None
        self.plot = None
        self.curr_num_nodes = None
        self.root = None
        self.curr = None
        self.node_matrix = None
        self.pos_x = None
        self.pos_y = None
        self.temp_color = '#66ce62'
        self.root_color = '#006400'
        self.curr_color = '#d00000'
        self.middle_color = '#25B0B0'
        self.default_node_size = 200
        self.configure_layout()

    def pick_event(self, event):
        if not hasattr(event, 'nodes') or not event.nodes:
            return

        node = event.nodes[0]
        if node == self.curr:
            return

        self.switch_node_colors(node)
        self.refresh_graph()

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
        self.curr_num_nodes = 1
        self.graph = nx.DiGraph()
        nodes = ['temp']

        self.graph.add_nodes_from(nodes)
        for _, node_attrs in self.graph.nodes(data=True):
            node_attrs['color'] = self.temp_color
            node_attrs['size'] = self.default_node_size

        self.plot = plot_network(self.graph, layout='spring', node_style=use_attributes())
        self.plot.set_picker(1)
        self.plot.axes.set_position([0.02, 0, 0.98, 1])
        self.canvas.draw_idle()

    def draw_graph(self):
        self.figure.clf()
        self.graph = nx.DiGraph()
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
        self.curr_num_nodes = len(nodes)
        self.graph.add_nodes_from(nodes)
        self.graph.add_edges_from(edges)
        for node, node_attrs in self.graph.nodes(data=True):
            if node == self.root:
                node_attrs['color'] = self.root_color
            elif node == self.curr:
                node_attrs['color'] = self.curr_color
            else:
                node_attrs['color'] = self.middle_color
            node_attrs['size'] = self.default_node_size

        for u, v, attrs in self.graph.edges.data():
            attrs['width'] = 1.5

        self.plot = plot_network(self.graph, layout=self.sequential_layout, node_style=use_attributes(), edge_style=use_attributes())
        self.plot.set_picker(1)
        self.plot.axes.set_position([0.02, 0, 0.98, 1])
        self.canvas.draw_idle()

    def sequential_layout(self, graph):
        self.pos_y = {
            self.root: 0
        }

        for key, values in self.index.items():
            for val in values:
                self.pos_y[val] = self.pos_y[key] + 1

        self.pos_x = {
            self.root: 0
        }

        for key, values in self.index.items():
            self.pos_x, _ = self.fill_pos_x(values, self.pos_x[self.root], self.pos_x)

        seq_layout = {}
        self.node_matrix = [[None for _ in range(len(dict.fromkeys(self.pos_y.values())))] for _ in range(len(dict.fromkeys(self.pos_x.values())))]
        for i, k in enumerate(graph.nodes.keys()):
            seq_layout[k] = [self.pos_x[k], self.pos_y[k]]
            self.node_matrix[self.pos_x[k]][self.pos_y[k]] = k

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

    def switch_node_colors(self, node):
        self.graph.nodes[node]['color'] = self.curr_color
        if self.curr == self.root:
            self.graph.nodes[self.curr]['color'] = self.root_color
        else:
            self.graph.nodes[self.curr]['color'] = self.middle_color
        self.curr = node

    def refresh_graph(self):
        self.plot.stale = True
        self.canvas.draw_idle()
        self.current_node.emit(self.curr)

    def move_up(self):
        curr_pos_x = self.pos_x[self.curr]
        curr_pos_y = self.pos_y[self.curr]
        if curr_pos_y + 1 < len(self.node_matrix[0]):
            node = self.node_matrix[curr_pos_x][curr_pos_y + 1]
            if node:
                self.switch_node_colors(node)
                self.refresh_graph()

    def move_down(self):
        curr_pos_x = self.pos_x[self.curr]
        curr_pos_y = self.pos_y[self.curr]
        if self.curr == self.root:
            return
        curr_pos_y -= 1
        node = self.node_matrix[curr_pos_x][curr_pos_y]
        while not node:
            curr_pos_x -= 1
            node = self.node_matrix[curr_pos_x][curr_pos_y]
        self.switch_node_colors(node)
        self.refresh_graph()

    def move_right(self):
        row = self.pos_x[self.curr]
        col = self.pos_y[self.curr]

        node = None

        while row + 1 < len(self.node_matrix) and not node:
            row += 1
            node = self.find_nearest_node_in_row(row, col)

        if node:
            self.switch_node_colors(node)
            self.refresh_graph()

    def find_nearest_node_in_row(self, row, col):
        node = self.node_matrix[row][col]
        if node:
            return node
        p1 = p2 = col
        while True:
            if p1 == len(self.node_matrix[0]) - 1 and p2 == 0:
                break

            if p1 < len(self.node_matrix[0]) - 1:
                p1 += 1
            if p2 > 0:
                p2 -= 1
            if self.node_matrix[row][p1]:
                return self.node_matrix[row][p1]
            if self.node_matrix[row][p2]:
                return self.node_matrix[row][p2]

        return None
