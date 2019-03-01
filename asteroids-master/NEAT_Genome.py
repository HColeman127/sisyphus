import math
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
    def __init__(self, input_size: int, output_size: int):
        self.nodes = {}
        self.connections = {}

        # add bias node to genome
        bias_node = Node(tag="bias", id=0)
        self.nodes[0] = bias_node

        # add input nodes to genome
        for i in range(1, 1+input_size):
            input_node = Node(tag="input", id=i)
            self.nodes[i] = input_node

        # add output nodes to genome
        for i in range(1+input_size, 1+input_size+output_size):
            output_node = Node(tag="output", id=i)
            output_node.depth = 1
            self.nodes[i] = output_node

    # node functions ------------------------------------------------
    def get_node_ids(self) -> list:
        return list(self.nodes.keys())

    def get_nodes(self) -> list:
        return list(self.nodes.values())

    def get_sorted_nodes_by_depth(self) -> list:
        node_depths = []
        node_ids = []
        for node in self.get_nodes():
            node_depths.append(node.depth)
            node_ids.append(node.id)

        sorted_pairs = sorted(zip(node_depths, node_ids))
        return [self.nodes[pair[1]] for pair in sorted_pairs]

    def get_node_out_connections(self, node_id: int) -> list:
        out_connections = []
        for connection in self.connections.values():
            if connection.expressed and connection.in_node == node_id:
                out_connections.append(connection)

        return out_connections

    def get_node_in_connections(self, node_id: int) -> list:
        out_connections = []
        for connection in self.connections.values():
            if connection.expressed and connection.out_node == node_id:
                out_connections.append(connection)

        return out_connections

    def insert_node(self, old_connection_id: int, next_node_id: int, next_connection_id: int) -> bool:

        # select and disable the old connection
        old_connection = self.connections[old_connection_id]
        if not old_connection.expressed:
            return False

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
        self.nodes[next_node_id] = new_node
        self.connections[next_connection_id] = new_connection_1
        self.connections[next_connection_id+1] = new_connection_2

        # recalculate node depths
        self.calculate_node_depths()
        return True

    def calculate_node_depths(self) -> None:
        node_queue = self.get_nodes()
        output_depths = []

        # initialize node depths
        for node in node_queue.copy():
            if node.tag in ["bias", "input"]:
                node.depth = 0
                node_queue.remove(node)
            else:
                node.depth = -1

        # while there are still undefined node depths
        while len(node_queue) > 0:
            for node in node_queue.copy():
                # get the depths of all input nodes
                input_depths = []
                for connection in self.get_node_in_connections(node.id):
                    input_depths.append(self.nodes[connection.in_node].depth)

                # if all input depths are defined
                if not input_depths:
                    node.depth = 1
                    node_queue.remove(node)
                elif min(input_depths) >= 0:
                    # define depth and remove from queue
                    node.depth = max(input_depths)+1
                    node_queue.remove(node)

                # if the depth of an output is found, add to list
                if node.tag == "output":
                    output_depths.append(node.depth)

        for node in self.get_nodes():
            if node.tag == "output":
                node.depth = max(output_depths)

    # connection functions ------------------------------------------
    def get_connections(self) -> list:
        return list(self.connections.values())

    def get_connection_ids(self):
        return list(self.connections.keys())

    def get_connection_by_nodes(self, in_node: int, out_node: int) -> Connection:
        for connection in self.get_connections():
            if connection.in_node == in_node and connection.out_node == out_node:
                return connection
        return None

    def get_expressed_connections(self) -> list:
        connections = []
        for connection in self.get_connections():
            if connection.expressed:
                connections.append(connection)
        return connections

    def add_connection(self, in_node: int, out_node: int, weight: float, next_connection_id: int) -> bool:
        # find existing connection, None if doesn't exist
        connection = self.get_connection_by_nodes(in_node=in_node, out_node=out_node)

        # if the connection exists
        if connection is not None:
            # express if not expressed
            if not connection.expressed:
                connection.expressed = True
            # either way, return False
            return False
        # if the depth of the in node is greater than the out node return False
        if self.nodes[in_node].depth == self.nodes[out_node].depth:
            #print(in_node, out_node)
            return False
        else:
            if self.nodes[in_node].depth > self.nodes[out_node].depth:
                out_node, in_node = in_node, out_node

        # create new connection and add to list
        new_connection = Connection(in_node=in_node, out_node=out_node, weight=weight, id=next_connection_id)
        self.connections[next_connection_id] = new_connection
        return True

    # evaluation functions ------------------------------------------
    def evaluate(self, sorted_nodes: list, inputs: list) -> list:
        node_queue = self.get_nodes()
        node_values = {}
        output = []

        # assign input values
        for node in sorted_nodes:
            if node.tag == "bias":
                node_values[node.id] = 1
            elif node.tag == "input":
                node_values[node.id] = inputs.pop(0)
            else:
                weighted_sum = 0.0
                for connection in self.get_node_in_connections(node.id):
                    weighted_sum += connection.weight * node_values[connection.in_node]

                value = self.activate(weighted_sum)
                node_values[node.id] = value

                if node.tag == "output":
                    output.append(round(node_values[node.id]))

        return output

    def activate(self, value: float) -> float:
        # sigmoid function
        output = 1.0/(1 + math.e**(-max(-50, min(50, value))))
        return output

    # drawing functions ---------------------------------------------
    def draw(self, block: bool) -> None:
        G, pos = self.create_digraph()
        plt.ion()

        if len(self.connections) > 0:
            edges, weights = zip(*nx.get_edge_attributes(G, 'weight').items())

            nx.draw(G, pos=pos, node_size=50, node_color='#5CB8B2', with_labels=False,
                    edgelist=edges, edge_color=weights, edge_cmap=plt.cm.get_cmap("bwr"))
        else:
            nx.draw(G, pos=pos, node_size=50, node_color='#5CB8B2', with_labels=False)

        plt.gcf().set_facecolor('#555555')
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0)
        #plt.draw()
        plt.show(block=block)
        plt.pause(0.0001)
        plt.cla()
        plt.clf()
        plt.ioff()


    def create_digraph(self):
        G = nx.DiGraph()
        G.add_nodes_from(self.get_node_ids())
        pos = {}
        current_output_height = 1

        sorted_nodes = self.get_sorted_nodes_by_depth()

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

                height = sum(input_heights)/len(input_heights)

                while (node.depth, height) in pos.values():
                    height += 1

                pos[node.id] = (node.depth, height)


        for edge in self.get_connections():
            if edge.expressed:
                G.add_edge(edge.in_node, edge.out_node, weight=-edge.weight)

        return G, pos
