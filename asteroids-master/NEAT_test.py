from NEAT_Individual import *
from MyGame import MyGame

try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle



def main():

    file_loc = "data/best_individuals_2019-02-26-181521.dat"
    file_pi = open(file_loc, 'rb')
    pop = pickle.load(file_pi)

    best = pop[0]
    for individual in pop:
        if individual.fitness > best.fitness:
            best = individual

    print("FITNESS:", best.fitness)
    print("ADJ FIT:", best.adj_fitness)
    best.draw(block=False)

    best.assess_fitness(max_trials=10, max_steps=1000, display=True)


main()