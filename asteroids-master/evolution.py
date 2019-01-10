import random
import numpy as np
import time
import math
from FitnessWrapper import FitnessWrapper as FW


# CONSTANTS
POPULATION_SIZE = 50
NUMBER_OF_TRIALS = 10
MAX_GENERATIONS = 100

SELECTION_PRESSURE = 2
MUTATION_RATE_0 = 0.05
MUTATION_STRENGTH = 0.5
CROSSOVER_WEIGHT = 0.25


def main():
    population = []
    next_generation = []
    best_individual = []
    best_fitness = 0
    mutation_rate = MUTATION_RATE_0

    # file names
    timestamp = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
    filename = "data/best_genome_log_" + timestamp + ".txt"
    filename2 = "data/best_fitness_log_" + timestamp + ".txt"
    filename3 = "data/average_fitness_log_" + timestamp + ".txt"

    print("--------------------------------------------------------")
    print("SAVING TO FILES:")
    print(filename)
    print(filename2)
    print(filename3)

    print("\n      POPULATION SIZE: %4d" % POPULATION_SIZE)
    print("     NUMBER OF TRIALS: %4d" % NUMBER_OF_TRIALS)
    print("      MAX GENERATIONS: %4d\n" % MAX_GENERATIONS)

    print("   SELECTION PRESSURE:", SELECTION_PRESSURE)
    print("INITIAL MUTATION RATE:", MUTATION_RATE_0)
    print("    MUTATION STRENGTH:", MUTATION_STRENGTH)
    print("     CROSSOVER WEIGHT:", CROSSOVER_WEIGHT, "\n")
    print("--------------------------------------------------------")
    print("SEEDING POPULATION...")
    start_time = time.time()
    population = generate_random_population(POPULATION_SIZE)
    print("POPULATION SEEDED!")
    print("SEEDING TIME: %ds" % (time.time() - start_time))
    print("--------------------------------------------------------")

    previous_diversity = get_diversity(population)

    # increment generations
    for gen in range(MAX_GENERATIONS):

        print("GENERATION:", gen)
        print("\nASSESSING POPULATION FITNESS...")
        start_time = time.time()
        fits = assess_gen_fits(population)
        print("FITNESS ASSESSED")
        print("ASSESSMENT TIME: %ds\n" % (time.time() - start_time))

        ranked = rank_fit(population, fits)
        fits.sort()

        f3 = open(filename3, "a")
        average = np.mean(fits)
        f3.write("%d\n" % average)
        f3.close()
        diversity = get_diversity(population)
        delta_diversity = diversity - previous_diversity

        print("  [GENERATION] AVERAGE FITNESS: %.0f" % average)
        print("               DIVERSITY: %f" % diversity)
        print("               CHANGE IN DIVERSITY: %f" % delta_diversity)
        previous_diversity = diversity

        if max(fits) > best_fitness:
            best_individual = ranked[-1]
            best_fitness = max(fits)
            print("\n  [INDIVIDUAL] BEST FITNESS:", best_fitness)
            print("               GENOME:", best_individual)
            best_numpy = np.asarray(best_individual)

            f1 = open(filename, "a")
            writable = np.array2string(best_numpy, separator=",", max_line_width=5000,
                                       formatter={'float_kind': lambda x: "%f" % x})
            f1.write(writable)
            f1.close()

            f2 = open(filename2, "a")
            f2.write(str(best_fitness))
            f2.close()

        # seed the next generation

        next_generation.clear()

        print("\nSEEDING NEXT GENERATION...")

        #mutation_rate = -delta_diversity

        print("               MUTATION RATE: %f" % mutation_rate)

        for i in range(round(POPULATION_SIZE / 2)):

            parent_one = select_parent(ranked, fits)
            parent_two = select_parent(ranked, fits)
            # print("PARENT 1:", parent_one)
            # print("PARENT 2:", parent_two)

            while parent_one == parent_two:
                parent_two = select_parent(ranked, fits)

            child_one, child_two = crossover(parent_one, parent_two)

            mutate(child_one, mutation_rate)
            mutate(child_one, mutation_rate)

            next_generation.append(child_one)
            next_generation.append(child_two)

        population.clear()
        population = next_generation.copy()

        print("NEXT GENERATION SEEDED")
        print("--------------------------------------------------------")
    # exit loop at generation max

    print("CLOSING")
    print(best_individual)

# =================================================================
# =    HELPER METHODS                                             =
# =================================================================


def select_parent(population, fits):
    fitness_percentages = gen_probability_distribution(fits)
    x = random.uniform(0, 1)

    for index in range(len(population)):
        if x < fitness_percentages[index]:
            return population[index]


def gen_probability_distribution(fits):
    weighted_fits = [fit**SELECTION_PRESSURE for fit in fits]
    total_fitness = sum(weighted_fits)

    fit_percents = [fit/total_fitness for fit in weighted_fits]

    percent = 0
    fit_dist = []
    for fit in fit_percents:
        percent += fit
        fit_dist.append(percent)

    return fit_dist


def rank_fit(generation, fits):
    return [pair[1] for pair in sorted(zip(fits, generation))]


def assess_gen_fits(generation):
    fit_test = FW(display=False)

    # actual fitness
    return [fit_test.get_fitness(individual, games_max=NUMBER_OF_TRIALS) for individual in generation]

    # random fitness. faster running for testing other features
    # return [random.randint(0, 100) for individual in generation]


def get_diversity(pop):
    return np.average([math.sqrt(np.var(np.array(pop)[:, i])) for i in range(len(pop[0]))])


def generate_random_population(size=100):
    return [generate_random_individual(-1, 1, 116) for _ in range(size)]


def generate_random_individual(min_value=-1, max_value=1, length=116):
    return [random.uniform(min_value, max_value) for _ in range(length)]


def crossover(genome_one, genome_two):
    """ accepts: GENES - two lists of floats of length n (one dimensional)
        outputs: a new list of the same length which is a crossover
                of the two genes entered
        NOTE: Recombination method: The new list has a 50% chance of
                receiving a given float (gene) from genes one or from genes two"""

    child1 = []
    child2 = []

    assert len(genome_one) == len(genome_two), "CROSSING OVER GENES OF DIFFERENT SIZE"

    for i in range(len(genome_one)):
        child1.append(CROSSOVER_WEIGHT*genome_one[i] + (1-CROSSOVER_WEIGHT)*genome_two[i])
        child2.append(CROSSOVER_WEIGHT*genome_two[i] + (1-CROSSOVER_WEIGHT)*genome_one[i])

    return child1, child2


def mutate(genetic_code, mutation_rate, max_value=1, min_value=-1):
    """ accepts:    GENETIC_CODE input of an n length list of floats
                    MUTATION_RATE the chance any given float (gene) mutates.
                                between zero and one (default is .05)
                    VARIANCE the size of one standard deviation for generating
                                the new value from a Gaussian distribution (Default is .1)
                    MAX: the max value of any float on the list (default is 1)
                    MIN: the min value of any float on the list (default is -1)
        NOTE: This does not return a copy of the array entered, it edits that array"""

    for i in range(len(genetic_code)):
        if random.uniform(0, 1) <= mutation_rate:
            # assigns new value using normal distribution, staying in upper and lower limits
            genetic_code[i] = max(min_value, min(max_value, random.gauss(genetic_code[i], MUTATION_STRENGTH)))


# run main
main()
