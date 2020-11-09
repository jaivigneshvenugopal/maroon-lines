from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backend_bases import MouseButton
from grave import plot_network
from grave.style import use_attributes
import matplotlib.pyplot as plt
import networkx as nx
from IPython import embed


class Timeline(QMainWindow):
    """
    Graphical component of the editor that visualizes the various versions of a file.

    """

    # Signals
    request_to_change_node = QtCore.pyqtSignal(str)
    curr_node_changed = QtCore.pyqtSignal(str)
    num_nodes_changed = QtCore.pyqtSignal(int)

    # Constants
    ROOT_NODE_COLOR = '#006400'
    CURR_NODE_COLOR = '#d00000'
    UNSAVED_NODE_COLOR = '#FF7F7F'
    DEFAULT_NODE_SIZE = 200
    DEFAULT_NODE_COLOR = '#25B0B0'
    FIGURE_BACKGROUND_COLOR = '#fff0f0'
    UNSAVED_NODE = 'unsaved_node'

    def __init__(self):
        super(Timeline, self).__init__()

        # Widget-related properties
        self.figure = None
        self.canvas = None
        self.plot = None

        self.index = None

        # Graph plot related properties
        self.graph = None
        self.graph_matrix = None
        self.pos_x = None
        self.pos_y = None
        self.root = None
        self.curr = None
        self.adopts = None
        self.num_nodes = None

        # Instantiate relevant components
        self.configure_figure_and_canvas()
        self.configure_layout_and_show()

    def configure_figure_and_canvas(self):
        self.figure = plt.figure()
        self.figure.set_facecolor(self.FIGURE_BACKGROUND_COLOR)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('pick_event', self.pick_event)

    def configure_layout_and_show(self):
        self.setCentralWidget(self.canvas)
        self.show()

    def reset_graph_properties(self):
        self.graph = None
        self.graph_matrix = None
        self.pos_x = None
        self.pos_y = None
        self.root = None
        self.curr = None
        self.adopts = None
        self.num_nodes = None

    def render_graph(self, index):
        self.index = index
        self.build_graph()

    def build_graph(self):
        self.reset_graph_properties()
        self.figure.clf()
        self.graph = nx.DiGraph()

        if self.index:
            self.extract_critical_nodes()
            self.add_nodes_and_edges()
            self.assign_node_positions()
        else:
            self.add_temp_node()

        self.num_nodes = len(self.graph.nodes())
        self.num_nodes_changed.emit(self.num_nodes)
        self.configure_node_and_edge_aesthetics()
        self.plot_graph()

    def plot_graph(self):
        layout = self.sequential_layout if self.index else 'spring'
        self.plot = plot_network(self.graph,
                                 layout=layout,
                                 node_style=use_attributes(),
                                 edge_style=use_attributes())
        self.plot.set_picker(1)
        self.plot.axes.set_position([0.02, 0, 0.96, 1])

        # Set optimum x and y scale for sequential layout
        if layout == self.sequential_layout:
            max_y = len(set(self.pos_y.values()))
            if max_y < 12:
                self.plot.axes.set_ylim(-0.5, 12.5)

            max_x = len(set(self.pos_x.values()))
            if max_x < 6:
                self.plot.axes.set_xlim(-0.5, 5.5)

        self.canvas.draw_idle()

    def refresh_graph(self):
        """
        Use function when there is no need to re-instantiate graph related attributes.

        :return: None
        """

        # Marking stale as True informs the plot that it has to be redrawn, but I have no idea why I have to write it
        self.plot.stale = True
        self.canvas.draw_idle()
        self.curr_node_changed.emit(self.curr)

    def extract_critical_nodes(self):
        self.root = self.index['root']
        self.curr = self.index['curr']
        self.adopts = self.index['adopts']
        self.index.pop('root')
        self.index.pop('curr')
        self.index.pop('adopts')

    def add_temp_node(self):
        self.graph.add_node(self.UNSAVED_NODE)

    def add_nodes_and_edges(self):
        for key, values in self.index.items():
            self.graph.add_node(key)
            for val in values:
                self.graph.add_edge(key, val)

    def configure_node_and_edge_aesthetics(self):
        if not self.index:
            for _, node_attrs in self.graph.nodes(data=True):
                node_attrs['color'] = self.DEFAULT_NODE_COLOR
                node_attrs['size'] = self.get_node_size()
            return

        for node, node_attrs in self.graph.nodes(data=True):
            if node == self.root:
                node_attrs['color'] = self.ROOT_NODE_COLOR
            elif node == self.curr:
                node_attrs['color'] = self.CURR_NODE_COLOR
            elif node == self.UNSAVED_NODE:
                node_attrs['color'] = self.UNSAVED_NODE_COLOR
            else:
                node_attrs['color'] = self.DEFAULT_NODE_COLOR
            node_attrs['size'] = self.get_node_size()

        for u, v, attrs in self.graph.edges.data():
            attrs['width'] = 1.5
            if u == self.curr and v == self.UNSAVED_NODE:
                attrs['style'] = 'dotted'

        for edge in self.adopts:
            edge_attr = self.graph.edges[edge[0], edge[1]]
            edge_attr['style'] = 'dashed'

    def get_node_size(self):
        if not self.pos_x and not self.pos_y:
            return self.DEFAULT_NODE_SIZE

        x_capacity = 10
        y_capacity = 20
        max_x = len(set(self.pos_x.values()))
        max_y = len(set(self.pos_y.values()))
        if max_y < y_capacity and max_x < x_capacity:
            return self.DEFAULT_NODE_SIZE

        adjusted_node_x_size = (1 - ((max_x - x_capacity) * 0.03)) * self.DEFAULT_NODE_SIZE
        adjusted_node_y_size = (1 - ((max_y - y_capacity) * 0.01)) * self.DEFAULT_NODE_SIZE

        return max(30.0, min(adjusted_node_x_size, adjusted_node_y_size))

    # Slot
    def pick_event(self, event):
        if event.mouseevent.button != MouseButton.LEFT:
            return

        if hasattr(event, 'nodes') and event.nodes and event.nodes[0] != self.curr:
            self.request_to_change_node.emit(event.nodes[0])

    def sequential_layout(self, graph):
        seq_layout = {}

        # Build graph representation in 2D matrix form
        self.graph_matrix = [[None for _ in set(self.pos_y.values())] for _ in set(self.pos_x.values())]

        for key in graph.nodes.keys():
            seq_layout[key] = [self.get_pos_x_with_bias(key), self.get_pos_y_with_bias(key)]
            self.graph_matrix[self.pos_x[key]][self.pos_y[key]] = key if key != self.UNSAVED_NODE else None

        return seq_layout

    def get_pos_y_with_bias(self, key):
        """
        Bias is introduced to each node to center the graph on the canvas.

        :param key: node
        :return: positional value
        """
        max_y = len(set(self.pos_y.values()))
        if max_y > 13:
            return self.pos_y[key]
        else:
            return self.pos_y[key] + (6 - ((max_y - 1) * 0.5))

    def get_pos_x_with_bias(self, key):
        """
        Bias is introduced to each node to center the graph on the canvas.

        :param key: node
        :return: positional value
        """
        max_x = len(set(self.pos_x.values()))
        if max_x > 5:
            return self.pos_x[key]
        else:
            x = self.pos_x[key] + (2.5 - ((max_x - 1) * 0.5))
            return x

    def assign_node_positions(self):
        starting_pos_x = 0
        starting_pos_y = 0
        self.pos_x = {self.root: starting_pos_x}
        self.pos_y = {self.root: starting_pos_y}

        for parent, children in self.index.items():
            self.fill_pos_x(children, counter=starting_pos_x)
            self.fill_pos_y(parent, children)

    def fill_pos_x(self, children, counter):
        for child in children:
            if child not in self.pos_x:
                self.pos_x[child] = counter
                counter = self.fill_pos_x(self.index[child], counter)

        return counter if children else counter + 1

    def fill_pos_y(self, parent, children):
        for child in children:
            self.pos_y[child] = self.pos_y[parent] + 1

    def switch_node_colors(self, new_curr):
        self.graph.nodes[new_curr]['color'] = self.CURR_NODE_COLOR
        if self.curr == self.root:
            self.graph.nodes[self.curr]['color'] = self.ROOT_NODE_COLOR
        else:
            self.graph.nodes[self.curr]['color'] = self.DEFAULT_NODE_COLOR
        self.curr = new_curr
        self.refresh_graph()

    def move_up(self):
        curr_pos_x = self.pos_x[self.curr]
        curr_pos_y = self.pos_y[self.curr]
        if curr_pos_y + 1 < len(self.graph_matrix[0]):
            node = self.graph_matrix[curr_pos_x][curr_pos_y + 1]
            if node:
                self.switch_node_colors(node)

    def move_down(self):
        if self.curr == self.root:
            return

        curr_pos_x = self.pos_x[self.curr]
        curr_pos_y = self.pos_y[self.curr]
        curr_pos_y -= 1

        node = self.graph_matrix[curr_pos_x][curr_pos_y]
        while not node:
            curr_pos_x -= 1
            node = self.graph_matrix[curr_pos_x][curr_pos_y]

        self.switch_node_colors(node)

    def move_right(self):
        col = self.pos_x[self.curr]
        row = self.pos_y[self.curr]

        node = None
        while col + 1 < len(self.graph_matrix) and not node:
            col += 1
            node = self.find_nearest_node_in_col(col, row)

        if node:
            self.switch_node_colors(node)

    def move_left(self):
        col = self.pos_x[self.curr]
        row = self.pos_y[self.curr]

        node = None
        while col - 1 >= 0 and not node:
            col -= 1
            node = self.find_nearest_node_in_col(col, row)

        if node:
            self.switch_node_colors(node)

    def find_nearest_node_in_col(self, row, col):
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
