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
        self.game = gym.make("LunarLander-v2")
        self.display = display

    def get_fitness(self, params, games_max=20, step_max=5000, random_seed=None):
        graph = CompGraph(params)   # create graph with given parameters

        score = 0
        for game_number in range(games_max):

            obs = self.game.reset()
            done = False

            step_number = 0
            while not done:
                commands = int(round(graph.eval(obs)[0]*3))
                #print(commands)

                obs, reward, done, info = self.game.step(commands)
                if self.display:
                    self.game.render()
                step_number += 1

                score += reward



        fitness = score


        #print("  AVG SCORE: ", avg_score)
        #print("  AVG STEPS: ", avg_steps)
        #print("    HITRATE: ", hitrate)
        #print("SUM STD DEV:", sum_std_dev)

        return fitness

    def close(self):
        self.game.close()

