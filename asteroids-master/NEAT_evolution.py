from NEAT_Individual import *
import numpy as np
import threading
import time


# individuals
INPUT_SIZE = 3
OUTPUT_SIZE = 3

# population
POPULATION_SIZE = 50
NUMBER_OF_TRIALS = 10
MAX_STEPS = 200
MAX_GENERATIONS = 1000

# genetic
MUTATE_CONNECTION_ATTEMPTS = 10

# global variables (sue me)
global_node_number = INPUT_SIZE+OUTPUT_SIZE+1
global_connection_number = INPUT_SIZE*OUTPUT_SIZE+1


class AssessFit(threading.Thread):
    def __init__(self, individual: Individual):
        threading.Thread.__init__(self)
        self.individual = individual

    def run(self):
        self.individual.assess_fitness(max_trials=NUMBER_OF_TRIALS,
                                       max_steps=MAX_STEPS,
                                       display=True)
        print("#", end="", flush=True)


def main():
    global global_node_number
    global global_connection_number
    population = generate_random_population(POPULATION_SIZE)

    population[0].print_connections()

    for i in range(1000):
        mutate_node(population[0])
        mutate_connection(population[0])
        population[0].draw(stopping=False)





    #thread = AssessFit(population[0])
    #thread.start()
    #thread.join()



def generate_random_population(size: int) -> list:
    print("SEEDING POPULATION...")
    population = [Individual(input_size=INPUT_SIZE, output_size=OUTPUT_SIZE) for _ in range(size)]
    print("POPULATION SEEDED")
    print("--------------------------------------------------------")
    return population


def assess_gen_fits(generation: list) -> list:
    size = len(generation)
    print(end="|"+"-"*size+"|\n|")

    threads = []
    for individual in generation:
        thread = AssessFit(individual)
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    print("|")

    fits = [individual.fitness for individual in generation]
    return fits


def mutate_node(individual: Individual):
    global global_node_number
    global global_connection_number
    if individual.mutate_node(global_node_number, global_connection_number):
        global_node_number += 1
        global_connection_number += 2
    else:
        print("NODE FAILED")


def mutate_connection(individual: Individual):
    global global_connection_number
    if individual.mutate_connection(MUTATE_CONNECTION_ATTEMPTS, global_connection_number):
        global_connection_number += 1
    else:
        print("CONNECTION FAILED")


# run main
main()