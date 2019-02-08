from NEAT_Individual import *
import numpy as np
import time
from multiprocessing import Pool, Manager


# individuals
INPUT_SIZE = 11
OUTPUT_SIZE = 4

# population
POPULATION_SIZE = 50
NUMBER_OF_TRIALS = 10
MAX_STEPS = 200
MAX_GENERATIONS = 1000

# genetic


# speciation
COMPATIBILITY_THRESHOLD = 3.0

# global variables (sue me)
global_node_number = INPUT_SIZE+OUTPUT_SIZE+1
global_connection_number = INPUT_SIZE*OUTPUT_SIZE+1


def main():
    global global_node_number
    global global_connection_number
    population = generate_random_population(POPULATION_SIZE)

    fits = assess_gen_fits(population)

    print(fits)

    for individual in population:
        for i in range(10):
            mutate_node(individual)
            mutate_connection(individual)

    calc_adjusted_fitness(population[0], population)

    print(population[0].adj_fitness)




def generate_random_population(size: int) -> list:
    print("SEEDING POPULATION...")
    population = [Individual(input_size=INPUT_SIZE, output_size=OUTPUT_SIZE) for _ in range(size)]
    print("POPULATION SEEDED")
    print("--------------------------------------------------------")
    return population


def assess_fit(target: Individual) -> None:
    target.assess_fitness(max_trials=NUMBER_OF_TRIALS,  max_steps=MAX_STEPS, display=False)
    #print(target.fitness)
    print("#", end="", flush=True)


def assess_gen_fits(generation: list) -> list:
    start_time = time.time()
    print("ASSESSING POPULATION FITNESS...")
    print(end="|"+"-"*len(generation)+"|\n|")

    shared_gen = Manager().list(generation)

    print(generation)
    print(shared_gen)

    Pool(processes=10).map(assess_fit, shared_gen)

    #generation = list(shared_gen)

    print("|")
    print("POPULATION FITNESS ASSESSED")
    print("ASSESSMENT TIME: %ds\n" % (time.time() - start_time))

    for individual in shared_gen:
        print(individual.fitness)


    fits = [individual.fitness for individual in shared_gen]
    return fits


def compatibility_distance(a: Individual, b: Individual) -> float:
    return random.random()


def sharing_function(value: float) -> int:
    if value > COMPATIBILITY_THRESHOLD:
        return 0
    else:
        return 1


def calc_adjusted_fitness(target: Individual, population: list) -> None:
    species_size = 0
    for individual in population:
        species_size += sharing_function(compatibility_distance(target, individual))

    print(target.fitness)
    print(species_size)

    target.adj_fitness = target.fitness/species_size


def mutate_node(individual: Individual) -> None:
    global global_node_number
    global global_connection_number
    if individual.mutate_node(global_node_number, global_connection_number):
        global_node_number += 1
        global_connection_number += 2
    else:
        print("NODE FAILED")


def mutate_connection(individual: Individual) -> None:
    global global_connection_number
    if individual.mutate_connection(global_connection_number):
        global_connection_number += 1
    else:
        pass
        #print("CONNECTION FAILED")


# run main
if __name__ == '__main__':
    start_time = time.time()
    main()
    print("TOTAL EVALUATION TIME:", time.time()-start_time)
