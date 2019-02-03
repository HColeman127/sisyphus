import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx

class Connection(object):
    def __init__(self, in_node: int, out_node: int, weight: float, id: int):
        """ in_node(int) - start of connection
            out_node(int) - end of connection
            weight(float) - multiplies value passing through connection
            id(int) - connection innovation number"""

        self.in_node = in_node
        self.out_node = out_node
        self.weight = weight
        self.id = id
        self.expressed = True


class Node(object):
    def __init__(self, tag: str, id: int):
        """ activation(str) - the type of activation function which this node uses
            tag(str) - tells what type of node (input, output, hidden, or bias)
            id(int) - node innovation number"""

        self.tag = tag
        self.id = id
        self.depth = 0


class Genome(object):
    def __init__(self, input_size, output_size):
        self.nodes = []
        self.connections = []

        # add bias node to genome
        bias_node = Node(tag="bias", id=0)
        self.nodes.append(bias_node)

        # add input nodes to genome
        for i in range(1, 1+input_size):
            input_node = Node(tag="input", id=i)
            self.nodes.append(input_node)

        # add output nodes to genome
        for i in range(1+input_size, 1+input_size+output_size):
            output_node = Node(tag="output", id=i)
            output_node.depth = 1
            self.nodes.append(output_node)

    # node functions ------------------------------------------------
    def get_node_ids(self) -> list:
        node_ids = []
        for node in self.nodes:
            node_ids.append(node.id)
        return node_ids

    def get_output_node_ids(self) -> list:
        node_ids = []
        for node in self.nodes:
            if node.tag == "output":
                node_ids.append(node.id)
        return node_ids

    def has_node(self, node_id: int) -> bool:
        for node in self.nodes:
            if node.id == node_id:
                return True
        return False

    def get_node(self, node_id: int) -> Node:
        for node in self.nodes:
            if node.id == node_id:
                return node

    def get_node_out_connections(self, node_id: int) -> list:
        out_connections = []
        for connection in self.connections:
            if connection.expressed and connection.in_node == node_id:
                out_connections.append(connection)

        return out_connections

    def get_node_in_connections(self, node_id: int) -> list:
        out_connections = []
        for connection in self.connections:
            if connection.expressed and connection.out_node == node_id:
                out_connections.append(connection)

        return out_connections

    def insert_node(self, old_connection_id: int, next_node_id: int, next_connection_id: int) -> None:

        # select and disable the old connection
        old_connection = self.connections[old_connection_id]
        old_connection.expressed = False

        # create a new node
        new_node = Node(tag="hidden", id=next_node_id)

        # create new connections
        new_connection_1 = Connection(in_node=old_connection.in_node,
                                      out_node=next_node_id,
                                      weight=1,
                                      id=next_connection_id)

        new_connection_2 = Connection(in_node=next_node_id,
                                      out_node=old_connection.out_node,
                                      weight=old_connection.weight,
                                      id=next_connection_id+1)

        # add to lists
        self.nodes.append(new_node)
        self.connections.append(new_connection_1)
        self.connections.append(new_connection_2)

        # recalculate node depths
        self.calculate_node_depths()

    def calculate_node_depths(self):
        node_queue = self.nodes.copy()

        # initialize node depths
        for node in node_queue.copy():
            if node.tag in ["bias", "input"]:
                node.depth = 0
                node_queue.remove(node)
            else:
                node.depth = -1

        while len(node_queue) > 0:
            for node in node_queue.copy():
                # get the depths of all input nodes
                input_depths = []
                for connection in self.get_node_in_connections(node.id):
                    input_depths.append(self.get_node(connection.in_node).depth)

                # if all input depths are defined
                if min(input_depths) >= 0:
                    node.depth = max(input_depths)+1
                    node_queue.remove(node)

        output_depths = []
        for output_id in self.get_output_node_ids():
            output_depths.append(self.get_node(output_id).depth)

        for output_id in self.get_output_node_ids():
            self.get_node(output_id).depth = max(output_depths)

    # connection functions ------------------------------------------
    def get_connection(self, in_node: int, out_node: int) -> Connection:
        for connection in self.connections:
            if connection.in_node == in_node and connection.out_node == out_node:
                return connection
        return None

    def add_connection(self, in_node: int, out_node: int, weight: float, next_connection_id: int) -> bool:
        # find existing connection, None if doesn't exist
        connection = self.get_connection(in_node=in_node, out_node=out_node)

        # if the connection exists
        if connection is not None:
            # return False if already expressed
            if connection.expressed:
                print("EXISTING CONNECTION", in_node, "-->", out_node)
                return False
            # make change and return True if previously not expressed
            else:
                connection.expressed = True
                return True
        # if the depth of the in node is greater than the out node return False
        elif self.get_node(in_node).depth >= self.get_node(out_node).depth:
            print("INVALID CONNECTION", in_node, "-->", out_node)
            return False

        # create new connection and add to list
        new_connection = Connection(in_node=in_node, out_node=out_node, weight=weight, id=next_connection_id)
        self.connections.append(new_connection)
        return True

    # evaluation functions ------------------------------------------
    def evaluate(self, inputs: list) -> list:
        node_queue = self.nodes.copy()
        node_values = {}

        # assign bias (node 0) a value of 1
        node_values[0] = 1
        node_queue.pop(0)

        # assign input values
        for node in node_queue.copy():
            if node.tag == "input":
                node_values[node.id] = inputs.pop(0)
                node_queue.remove(node)

        # until all node values have been found
        while len(node_queue) > 0:
            for node in node_queue.copy():
                # check if all of the input values for a node are defined
                has_all_inputs = True
                input_connections = self.get_node_in_connections(node.id)

                for connection in input_connections:
                    if connection.in_node not in node_values:
                        has_all_inputs = False
                        break

                if has_all_inputs:
                    # compute weighted sum
                    weighted_sum = 0.0
                    for connection in input_connections:
                        weighted_sum += connection.weight * node_values[connection.in_node]

                    # activate value
                    value = self.activate(weighted_sum)
                    node_values[node.id] = value
                    node_queue.remove(node)

        #print(node_values)

        output = []
        for output_id in self.get_output_node_ids():
            output.append(node_values[output_id])

        return output

    def activate(self, value: float) -> float:
        # sigmoid function
        output = 1.0/(1 + math.e**(-value))
        return output

    # drawing functions ---------------------------------------------
    def draw(self):
        G = nx.DiGraph()
        G.add_nodes_from(self.get_node_ids())
        pos = {}
        current_output_height = 1

        # sort nodes by depth
        node_depths = [node.depth for node in self.nodes]
        sorted_nodes = []
        for pair in sorted(zip(node_depths, self.get_node_ids(), self.nodes.copy())):
            sorted_nodes.append(pair[2])

        for node in sorted_nodes:
            if node.tag in ["bias", "input"]:
                pos[node.id] = (node.depth, node.id)
            elif node.tag == "output":
                pos[node.id] = (node.depth, current_output_height)
                current_output_height += 1
            else:
                input_heights = []
                for connection in self.get_node_in_connections(node.id):
                    input_heights.append(pos[connection.in_node][1])

                pos[node.id] = (node.depth, sum(input_heights)/len(input_heights))

        for edge in self.connections:
            if edge.expressed:
                G.add_edge(edge.in_node, edge.out_node, weight=edge.weight)

        nx.draw(G,
                pos=pos,
                node_color='c',
                with_labels=True)

        plt.show()


