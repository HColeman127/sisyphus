from NEAT_Genome import *
from MyGame import MyGame
import random


class Individual(object):
    def __init__(self, input_size: int, output_size: int):
        # initialize genome
        self.genome = Genome(input_size=input_size, output_size=output_size)
        self.fitness = 0

        # initialize starting dense connections
        connection_number = 0
        for i in range(input_size):
            for j in range(output_size):
                self.genome.add_connection(in_node=(1 + i),
                                           out_node=(1 + input_size + j),
                                           weight=random.uniform(-1, 1),
                                           next_connection_id=connection_number)
                connection_number += 1

    def draw(self, block: bool):
        self.genome.draw(block)

    def mutate_weights(self, rate: float, strength: float) -> None:
        for connection in self.genome.get_connections():
            mu = connection.weight
            sigma = strength

            if random.random() < rate:
                new_weight = max(-1, min(1, random.gauss(mu, sigma)))
                connection.weight = new_weight

    def mutate_node(self, global_node_number: int, global_connection_number: int) -> bool:
        connection = random.choice(self.genome.get_expressed_connections())

        return self.genome.insert_node(old_connection_id=connection.id,
                                       next_node_id=global_node_number,
                                       next_connection_id=global_connection_number)

    def mutate_connection(self, global_connection_number: int) -> bool:
        node_id_list = self.genome.get_node_ids()
        return self.genome.add_connection(in_node=random.choice(node_id_list),
                                          out_node=random.choice(node_id_list),
                                          weight=random.uniform(-1, 1),
                                          next_connection_id=global_connection_number)

    def assess_fitness(self, max_trials: int, max_steps: int, display: bool) -> None:
        game = MyGame(display=display)
        node_list = self.genome.get_sorted_nodes_by_depth()
        scores = []
        steps = []
        hit_total = 0
        shot_total = 0

        for game_number in range(max_trials):
            playing, score, obs = game.reset()

            step_number = 0
            while playing and step_number < max_steps:
                commands = self.genome.evaluate(node_list, obs)
                playing, score, hits, shots, obs = game.step(commands)
                step_number += 1

            scores.append(score)
            steps.append(step_number)
            hit_total += hits
            shot_total += shots

        hitrate = hit_total / (shot_total + 1)
        avg_score = sum(scores) / len(scores)
        avg_steps = sum(steps) / len(steps)

        self.fitness = avg_score * avg_steps * (hitrate ** 4)

        # print("  AVG SCORE: ", avg_score)
        # print("  AVG STEPS: ", avg_steps)
        # print("    HITRATE: ", hitrate)
        # print("SUM STD DEV:", sum_std_dev)

    def print_connections(self):
        for connection in self.genome.get_connections():
            print("CONNECTION:", connection.id, "|", connection.in_node, "-->", connection.out_node)
            print("         WEIGHT:", connection.weight)
            print(      "EXPRESSED:", connection.expressed)
            print()
