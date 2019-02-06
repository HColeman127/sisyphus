from NEAT_Individual import *
import numpy as np
import time
from multiprocessing import Pool


# individuals
INPUT_SIZE = 11
OUTPUT_SIZE = 4

# population
POPULATION_SIZE = 50
NUMBER_OF_TRIALS = 100
MAX_STEPS = 200
MAX_GENERATIONS = 1000

# genetic


# speciation
COMPATIBILITY_THRESHOLD = 0.5

# global variables (sue me)
global_node_number = INPUT_SIZE+OUTPUT_SIZE+1
global_connection_number = INPUT_SIZE*OUTPUT_SIZE+1


def main():
    global global_node_number
    global global_connection_number
    population = generate_random_population(POPULATION_SIZE)

    #assess_gen_fits(population)



    #population[0].assess_fitness(max_trials=NUMBER_OF_TRIALS, max_steps=MAX_STEPS, display=True)

    for i in range(1000):
        population[0].draw(block=False)
        mutate_node(population[0])
        mutate_connection(population[0])




def generate_random_population(size: int) -> list:
    print("SEEDING POPULATION...")
    population = [Individual(input_size=INPUT_SIZE, output_size=OUTPUT_SIZE) for _ in range(size)]
    print("POPULATION SEEDED")
    print("--------------------------------------------------------")
    return population


def assess_fit(individual: Individual) -> None:
    individual.assess_fitness(max_trials=NUMBER_OF_TRIALS,  max_steps=MAX_STEPS, display=False)
    print("#", end="", flush=True)

def assess_gen_fits(generation: list) -> list:
    start_time = time.time()
    print("ASSESSING POPULATION FITNESS...")
    print(end="|"+"-"*len(generation)+"|\n|")

    Pool(processes=10).map(assess_fit, generation)

    print("|")
    print("POPULATION FITNESS ASSESSED")
    print("ASSESSMENT TIME: %ds\n" % (time.time() - start_time))
    fits = [individual.fitness for individual in generation]
    return fits

def compatibility_distance(a: Individual, b: Individual) -> float:
    return random.random()

def sharing_function(value: float) -> int:
     if value > COMPATIBILITY_THRESHOLD:
         return 0
     else:
         return 1

def calc_adjusted_fitness(individual: Individual, population: list) -> None:
    print("hello")


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