# imports
import time
import numpy as np
import math
from MyGame import MyGame
from CompGraph import CompGraph


class FitnessWrapper(object):
    GENOME_LENGTH = CompGraph.GENOME_LENGTH

    def __init__(self, display=False):
        # initializes game environment
        self.game = MyGame(display=display)

    def get_fitness(self, params, games_max=20, step_max=5000, random_seed=None):
        graph = CompGraph(params)   # create graph with given parameters
        scores = []
        steps = []
        hit_total = 0
        shot_total = 0

        for game_number in range(games_max):
            if random_seed is not None:
                self.game.random_seed(random_seed+game_number)

            playing, score, obs = self.game.reset()

            step_number = 0
            while playing and step_number < step_max:
                commands = graph.eval(obs)
                #print(commands)
                playing, score, hits, shots, obs = self.game.step(commands)
                step_number += 1

            scores.append(score)
            steps.append(step_number)
            hit_total += hits
            shot_total += shots

        hitrate = hit_total/(shot_total+1)
        avg_score = sum(scores)/len(scores)
        avg_steps = sum(steps)/len(steps)

        score_var = np.var(scores)
        step_var = np.var(steps)
        #score_std_dev = math.sqrt(score_var)
        sum_std_dev = math.sqrt(score_var + step_var)

        fitness = avg_score*avg_steps*(hitrate**4)/sum_std_dev


        #print("  AVG SCORE: ", avg_score)
        #print("  AVG STEPS: ", avg_steps)
        #print("    HITRATE: ", hitrate)
        #print("SUM STD DEV:", sum_std_dev)

        return fitness

