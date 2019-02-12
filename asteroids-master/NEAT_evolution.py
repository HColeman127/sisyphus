from NEAT_Individual import *
import numpy as np
import time
from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager


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
COMPATIBILITY_THRESHOLD = 0.7

# global variables (sue me)
global_node_number = INPUT_SIZE+OUTPUT_SIZE+1
global_connection_number = INPUT_SIZE*OUTPUT_SIZE+1


def main():
    global global_node_number
    global global_connection_number

    population = generate_random_population(POPULATION_SIZE)

    for individual in population:
        for i in range(10):
            mutate_node(individual)
            mutate_connection(individual)

    fits = assess_gen_fits(population)
    adj_fits = calc_gen_adj_fits(population)

    print(fits)
    print(adj_fits)


def get_compatibility_distance(ind_one: Individual, ind_two: Individual) -> float:

    excess_gene_weight = 1
    disjoint_gene_weight = 1
    weight_diff_weight = 0.4
    comp_distance = 0

    ind_one_connections = ind_one.genome.get_connection_ids()
    ind_two_connections = ind_two.genome.get_connection_ids()

    disjoints = 0
    excesses = 0

    #print(ind_one_connections)
    #print(ind_two_connections)

    # -- calc num of disjoints and excesses
    max_val = max(max(ind_one_connections), max(ind_two_connections))
    min_val = min(max(ind_one_connections), max(ind_two_connections))

    #print(max_val, min_val)

    for count in range(min_val+1):
        if (count in ind_one_connections) ^ (count in ind_two_connections):
                disjoints += 1


    ran = range(min_val+1, max_val+1)
    one = len(set(ran).intersection(ind_one_connections))
    two = len(set(ran).intersection(ind_two_connections))
    #print(one,two)
    excesses = max(one,two)
    # -- end

    # -- calc avg. weight differences of matching connections
    matching = set(ind_one_connections).intersection(ind_two_connections)
    number = len(matching)
    sum = 0

    for num in matching:
        weight1 = ind_one.genome.connections[num].weight
        weight2 = ind_two.genome.connections[num].weight
        difference = weight1 - weight2
        sum += difference

    average = sum/number

    N = max(len(ind_one_connections), len(ind_two_connections)) # N is the size of the larger genome
    compatibility_distance = (excess_gene_weight*excesses)/N + (disjoint_gene_weight*disjoints)/N + weight_diff_weight * average

    return compatibility_distance


def generate_random_population(size: int) -> list:
    print("SEEDING POPULATION...")
    population = [Individual(input_size=INPUT_SIZE, output_size=OUTPUT_SIZE) for _ in range(size)]
    print("POPULATION SEEDED")
    print("--------------------------------------------------------")
    return population


def assess_fit(target: Individual) -> None:
    target.assess_fitness(max_trials=NUMBER_OF_TRIALS,  max_steps=MAX_STEPS, display=False)
    print("#", end="", flush=True)


def assess_gen_fits(generation: list) -> list:
    start_time = time.time()
    print("ASSESSING POPULATION FITNESS...")
    print(end="|"+"-"*len(generation)+"|\n|")

    for individual in generation:
        assess_fit(individual)

    print("|")
    print("POPULATION FITNESS ASSESSED")
    print("ASSESSMENT TIME: %ds\n" % (time.time() - start_time))

    fits = [individual.fitness for individual in generation]
    return fits


def sharing_function(value: float) -> int:
    if value > COMPATIBILITY_THRESHOLD:
        return 0
    else:
        return 1


def calc_adj_fit(target: Individual, population: list) -> None:
    species_size = 0
    for individual in population:
        species_size += sharing_function(get_compatibility_distance(target, individual))

    target.adj_fitness = target.fitness/species_size


def calc_gen_adj_fits(generation: list) -> list:
    print("CALCULATING ADJUSTED FITNESSES...")
    print(end="|" + "-" * len(generation) + "|\n|")
    for individual in generation:
        calc_adj_fit(individual, generation)
        print("#", end="", flush=True)

    adj_fits = [individual.adj_fitness for individual in generation]

    print("|")
    print("ADJUSTED FITNESSES CALCULATED")
    return adj_fits


def mutate_node(individual: Individual) -> None:
    global global_node_number
    global global_connection_number
    if individual.mutate_node(global_node_number, global_connection_number):
        global_node_number += 1
        global_connection_number += 2
    else:
        pass
        #("NODE FAILED")


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
    print("\n\nTOTAL EVALUATION TIME:", time.time()-start_time)
