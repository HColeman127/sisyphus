# imports
import time
from MyGame import MyGame
from CompGraph import CompGraph


class FitnessWrapper(object):
    GENOME_LENGTH = CompGraph.GENOME_LENGTH

    def __init__(self, display=False):
        # initializes game environment
        self.game = MyGame(display=display)


    def get_fitness(self, params, games_max=20, step_max=5000):
        graph = CompGraph(params)   # create graph with given parameters
        scores = []
        hit_total = 0
        shot_total = 0

        #self.game.random_seed(123456)

        for game_number in range(games_max):
            playing, score, obs = self.game.reset()

            # game will play until lost or until max_step is reached
            step_number = 0
            while playing and step_number < step_max:
                # gets actions and passes into environment
                commands = graph.eval(obs)
                #print(obs)
                #time.sleep(0.1)
                playing, score, hits, shots, obs = self.game.step(commands)


                # increment step number
                step_number += 1

            scores.append(score)
            hit_total += hits
            shot_total += shots

        # returns the average score times the proportion of nonzero scores
        return (sum(scores)/len(scores))*(1 - scores.count(0)/games_max)*hit_total/max(1, shot_total)

    def get_mean_convergence(self, params, games_max=100, step_max=5000):
        graph = CompGraph(params)  # create graph with given parameters
        total_score = 0
        mean_scores = []

        for game_number in range(1, games_max+1):
            playing, score, obs = self.game.reset()

            # game will play until lost or until max_step is reached
            step_number = 0
            while playing and step_number < step_max:
                # gets actions and passes into environment
                commands = graph.eval(obs)
                playing, score, obs = self.game.step(commands)

                step_number += 1

            total_score += score
            mean_scores.append(total_score//game_number)

        # returns the average score
        return mean_scores
