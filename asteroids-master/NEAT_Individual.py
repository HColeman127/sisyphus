from NEAT_Genome import *
import random

INPUT_SIZE = 2
OUTPUT_SIZE = 2

global_node_number = INPUT_SIZE+OUTPUT_SIZE+1
global_connection_number = 0

jeremy = Genome(INPUT_SIZE, OUTPUT_SIZE)


for i in range(INPUT_SIZE):
    for j in range(OUTPUT_SIZE):
        jeremy.add_connection(1+i, 1+INPUT_SIZE+j, 0.1, global_connection_number)
        global_connection_number += 1

jeremy.insert_node(0, global_node_number, global_connection_number)
global_node_number += 1
global_connection_number += 2

jeremy.insert_node(3, global_node_number, global_connection_number)
global_node_number += 1
global_connection_number += 2

jeremy.insert_node(4, global_node_number, global_connection_number)
global_node_number += 1
global_connection_number += 2


jeremy.add_connection(0, 7, 0.1, global_connection_number)
global_connection_number += 1

jeremy.add_connection(2, 5, 0.1, global_connection_number)
global_connection_number += 1

jeremy.add_connection(1, 5, 0.1, global_connection_number)
global_connection_number += 1

jeremy.add_connection(6, 5, 0.1, global_connection_number)
global_connection_number += 1

"""
for node in jeremy.nodes:
    print(node.id, node.tag, node.depth)

for connection in jeremy.connections:
    print("CONNECTION:", connection.id, "|", connection.in_node, "-->", connection.out_node)
    print("         WEIGHT:", connection.weight)
    print("      EXPRESSED:", connection.expressed)
    print()
"""

inputs = [2, 3]

jeremy.draw()



"""
for i in range(1000):
    for j in range(1000):
        jeremy.evaluate([i, j])"""



