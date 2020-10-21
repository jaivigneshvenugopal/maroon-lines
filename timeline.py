import PyQt5
from PyQt5.QtWidgets import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import networkx as nx

from grave import plot_network
from grave.style import use_attributes
from IPython import embed


class Timeline(QMainWindow):

    # Signals
    curr_node_changed = PyQt5.QtCore.pyqtSignal(str)
    num_nodes_changed = PyQt5.QtCore.pyqtSignal(str)

    def __init__(self):
        super(Timeline, self).__init__()

        # Widget-related properties
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.plot = None

        # Graph-related properties
        self.index = None
        self.graph = None
        self.num_nodes = None
        self.root = None
        self.curr = None
        self.adopts = None
        self.pos_x = None
        self.pos_y = None
        self.graph_matrix = None

        # Graph-node related properties
        self.root_node_color = '#006400'
        self.curr_node_color = '#d00000'
        self.default_node_color = '#25B0B0'
        self.temp_node_color = '#66ce62'
        self.default_node_size = 200

        # Instantiate relevant components
        self.configure_figure_and_canvas()
        self.configure_layout_and_show()

    def configure_figure_and_canvas(self):
        self.figure.set_facecolor('#fff0f0')
        self.canvas.mpl_connect('pick_event', self.pick_event)

    def configure_layout_and_show(self):
        self.setCentralWidget(self.canvas)
        self.show()

    def pick_event(self, event):
        if not hasattr(event, 'nodes') or not event.nodes or event.nodes[0] == self.curr:
            return

        self.switch_node_colors(event.nodes[0])
        self.refresh_graph()

    def render_graph(self, index):
        self.index = index
        eval('self.init_graph()')

        self.num_nodes_changed.emit(str(self.num_nodes))

    def init_graph(self):
        self.figure.clf()
        self.graph = nx.DiGraph()

        if not self.index:
            self.graph.add_nodes_from(['temp_node'])
            self.num_nodes = 1
        else:
            self.root = self.index['root']
            self.curr = self.index['curr']
            self.adopts = self.index['adopts']
            self.index.pop('root')
            self.index.pop('curr')
            self.index.pop('adopts')
            self.num_nodes = len(self.index.items())

            for key, values in self.index.items():
                self.graph.add_node(key)
                for val in values:
                    self.graph.add_edge(key, val)

            self.assign_node_positions()

        self.configure_node_and_edge_aesthetics()
        self.plot_graph()

    def configure_node_and_edge_aesthetics(self):
        if not self.index:
            for _, node_attrs in self.graph.nodes(data=True):
                node_attrs['color'] = self.temp_node_color
                node_attrs['size'] = self.default_node_size
        else:
            for node, node_attrs in self.graph.nodes(data=True):
                if node == self.root:
                    node_attrs['color'] = self.root_node_color
                elif node == self.curr:
                    node_attrs['color'] = self.curr_node_color
                else:
                    node_attrs['color'] = self.default_node_color
                node_attrs['size'] = self.default_node_size

            for u, v, attrs in self.graph.edges.data():
                attrs['width'] = 1.5

            for edge in self.adopts:
                edge_attr = self.graph.edges[edge[0], edge[1]]
                edge_attr['style'] = 'dotted'

    def plot_graph(self):
        if self.index:
            layout = self.sequential_layout
        else:
            layout = 'spring'

        self.plot = plot_network(self.graph,
                                 layout=layout,
                                 node_style=use_attributes(),
                                 edge_style=use_attributes())
        self.plot.set_picker(1)
        self.plot.axes.set_position([0.1, 0, 0.8, 1])
        self.canvas.draw_idle()

    def sequential_layout(self, graph):
        seq_layout = {}

        for key in graph.nodes.keys():
            # Set x & y position for key
            seq_layout[key] = [self.pos_x[key], self.pos_y[key]]
            # Store key in corresponding x & y position of graph matrix
            self.graph_matrix[self.pos_x[key]][self.pos_y[key]] = key

        return seq_layout

    def assign_node_positions(self):
        # Fill in correct x & y positions of all nodes
        initial_pos = 0
        self.pos_x = {self.root: initial_pos}
        self.pos_y = {self.root: initial_pos}

        for key, values in self.index.items():
            self.fill_pos_x(values, counter=initial_pos)
            self.fill_pos_y(key, values)
        self.graph_matrix = [[None for _ in set(self.pos_y.values())] for _ in set(self.pos_x.values())]

    def fill_pos_x(self, values, counter):
        for val in values:
            if val not in self.pos_x:
                self.pos_x[val] = counter
                counter = self.fill_pos_x(self.index[val], counter)
        if values:
            return counter
        else:
            return counter + 1

    def fill_pos_y(self, key, values):
        for val in values:
            self.pos_y[val] = self.pos_y[key] + 1

    def switch_node_colors(self, node):
        self.graph.nodes[node]['color'] = self.curr_node_color
        if self.curr == self.root:
            self.graph.nodes[self.curr]['color'] = self.root_node_color
        else:
            self.graph.nodes[self.curr]['color'] = self.default_node_color
        self.curr = node

    def refresh_graph(self):
        self.plot.stale = True
        self.canvas.draw_idle()
        self.curr_node_changed.emit(self.curr)

    def move_up(self):
        curr_pos_x = self.pos_x[self.curr]
        curr_pos_y = self.pos_y[self.curr]
        if curr_pos_y + 1 < len(self.graph_matrix[0]):
            node = self.graph_matrix[curr_pos_x][curr_pos_y + 1]
            if node:
                self.switch_node_colors(node)
                self.refresh_graph()

    def move_down(self):
        curr_pos_x = self.pos_x[self.curr]
        curr_pos_y = self.pos_y[self.curr]
        if self.curr == self.root:
            return
        curr_pos_y -= 1
        node = self.graph_matrix[curr_pos_x][curr_pos_y]
        while not node:
            curr_pos_x -= 1
            node = self.graph_matrix[curr_pos_x][curr_pos_y]
        self.switch_node_colors(node)
        self.refresh_graph()

    def move_right(self):
        row = self.pos_x[self.curr]
        col = self.pos_y[self.curr]

        node = None

        while row + 1 < len(self.graph_matrix) and not node:
            row += 1
            node = self.find_nearest_node_in_row(row, col)

        if node:
            self.switch_node_colors(node)
            self.refresh_graph()

    def move_left(self):
        row = self.pos_x[self.curr]
        col = self.pos_y[self.curr]

        node = None

        while row - 1 >= 0 and not node:
            row -= 1
            node = self.find_nearest_node_in_row(row, col)

        if node:
            self.switch_node_colors(node)
            self.refresh_graph()

    def find_nearest_node_in_row(self, row, col):
        node = self.graph_matrix[row][col]
        if node:
            return node
        p1 = p2 = col
        while True:
            if p1 == len(self.graph_matrix[0]) - 1 and p2 == 0:
                break

            if p1 < len(self.graph_matrix[0]) - 1:
                p1 += 1
            if p2 > 0:
                p2 -= 1
            if self.graph_matrix[row][p1]:
                return self.graph_matrix[row][p1]
            if self.graph_matrix[row][p2]:
                return self.graph_matrix[row][p2]

        return None
