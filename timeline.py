import PyQt5
import matplotlib.pyplot as plt
import networkx as nx
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from grave import plot_network
from grave.style import use_attributes
from IPython import embed


class Timeline(QMainWindow):

    # Signals
    curr_node_changed = PyQt5.QtCore.pyqtSignal(str)
    num_nodes_changed = PyQt5.QtCore.pyqtSignal(str)

    # Constants
    ROOT_NODE_COLOR = '#006400'
    CURR_NODE_COLOR = '#d00000'
    TEMP_NODE_COLOR = '#66ce62'
    DEFAULT_NODE_SIZE = 200
    DEFAULT_NODE_COLOR = '#25B0B0'
    FIGURE_BACKGROUND_COLOR = '#fff0f0'

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
        self.root_node_color = self.ROOT_NODE_COLOR
        self.curr_node_color = self.CURR_NODE_COLOR
        self.temp_node_color = self.TEMP_NODE_COLOR
        self.default_node_color = self.DEFAULT_NODE_COLOR
        self.default_node_size = self.DEFAULT_NODE_SIZE

        # Instantiate relevant components
        self.configure_figure_and_canvas()
        self.configure_layout_and_show()

    def configure_figure_and_canvas(self):
        self.figure.set_facecolor(self.FIGURE_BACKGROUND_COLOR)
        self.canvas.mpl_connect('pick_event', self.pick_event)

    def configure_layout_and_show(self):
        self.setCentralWidget(self.canvas)
        self.show()

    def render_graph(self, index):
        self.index = index
        self.build_graph()

    def build_graph(self):
        self.figure.clf()
        self.graph = nx.DiGraph()

        if not self.index:
            self.graph.add_node('temp_node')
            self.num_nodes = 1
        else:
            self.extract_critical_nodes()
            self.add_nodes_and_edges()
            self.assign_node_positions()
            self.num_nodes = len(self.graph.nodes())

        self.num_nodes_changed.emit(str(self.num_nodes))
        self.configure_node_and_edge_aesthetics()
        self.plot_graph()

    def plot_graph(self):
        layout = self.sequential_layout if self.index else 'spring'
        self.plot = plot_network(self.graph,
                                 layout=layout,
                                 node_style=use_attributes(),
                                 edge_style=use_attributes())
        self.plot.set_picker(1)
        x = 0
        len_x = 1
        y = 0
        len_y = 1

        if self.index:
            max_y = len(self.pos_y.values())
            if 1 < max_y < 10:
                y = 0.35 - ((max_y - 2) * 0.05)
                len_y = 1 - (2 * y)
            max_x = len(self.pos_x.values())
            if 1 < max_x < 10:
                x = 0.45 - ((max_x - 2) * 0.05)
                len_x = 1 - (2 * x)

        self.plot.axes.set_position([x, y, len_x, len_y])
        self.canvas.draw_idle()

    def refresh_graph(self):
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

    def add_nodes_and_edges(self):
        if self.index:
            for key, values in self.index.items():
                self.graph.add_node(key)
                for val in values:
                    self.graph.add_edge(key, val)

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

    def pick_event(self, event):
        if hasattr(event, 'nodes') and event.nodes and event.nodes[0] != self.curr:
            self.switch_node_colors(event.nodes[0])

    def sequential_layout(self, graph):
        seq_layout = {}
        self.graph_matrix = [[None for _ in set(self.pos_y.values())] for _ in set(self.pos_x.values())]

        for key in graph.nodes.keys():
            seq_layout[key] = [self.pos_x[key], self.pos_y[key]]
            self.graph_matrix[self.pos_x[key]][self.pos_y[key]] = key

        return seq_layout

    def assign_node_positions(self):
        starting_pos = 0
        self.pos_x = {self.root: starting_pos}
        self.pos_y = {self.root: starting_pos}

        for parent, children in self.index.items():
            self.fill_pos_x(children, counter=starting_pos)
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
        self.graph.nodes[new_curr]['color'] = self.curr_node_color
        self.graph.nodes[self.curr]['color'] = \
            self.root_node_color if self.curr == self.root else self.default_node_color
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
        row = self.pos_x[self.curr]
        col = self.pos_y[self.curr]

        node = None
        while row + 1 < len(self.graph_matrix) and not node:
            row += 1
            node = self.find_nearest_node_in_row(row, col)

        if node:
            self.switch_node_colors(node)

    def move_left(self):
        row = self.pos_x[self.curr]
        col = self.pos_y[self.curr]

        node = None
        while row - 1 >= 0 and not node:
            row -= 1
            node = self.find_nearest_node_in_row(row, col)

        if node:
            self.switch_node_colors(node)

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
