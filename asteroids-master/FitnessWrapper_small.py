# imports
import time
import numpy as np
import math
from CompGraph import CompGraph
from MyGame import MyGame
import gym
#import universe




class FitnessWrapper(object):
    GENOME_LENGTH = CompGraph.GENOME_LENGTH

    def __init__(self, display=False):
        # initializes game environment
        self.game = gym.make("CartPole-v1")
        self.display = display

    def get_fitness(self, params, games_max=20, step_max=5000, random_seed=None):
        graph = CompGraph(params)   # create graph with given parameters

        steps = []
        for game_number in range(games_max):

            obs = self.game.reset()
            playing = True

            step_number = 0
            while playing:
                commands = int(graph.eval(obs)[0])
                obs, reward, done, info = self.game.step(commands)
                if self.display:
                    self.game.render()
                step_number += 1

                if not (-2.4 < obs[0] < 2.4) or \
                   not (-0.2 < obs[2] < 0.2) or \
                   step_number > step_max:

                    playing = False

            steps.append(step_number)


        avg_steps = sum(steps)/len(steps)

        fitness = avg_steps


        #print("  AVG SCORE: ", avg_score)
        #print("  AVG STEPS: ", avg_steps)
        #print("    HITRATE: ", hitrate)
        #print("SUM STD DEV:", sum_std_dev)

        return fitness

    def close(self):
        self.game.close()

