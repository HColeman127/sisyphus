import random
import numpy as np
import time
import math
from FitnessWrapper import FitnessWrapper as fw


# CONSTANTS
POPULATION_SIZE = 30
NUMBER_OF_TRIALS = 10
MAX_GENERATIONS = 1000

CROSSOVER_WEIGHT = 0.25
MUTATION_RATE_0 = 0.001
MUTATION_STRENGTH_0 = 0.1
SELECTION_PRESSURE_0 = 0


def main():
    population = []
    next_generation = []
    best_individual = []
    avg_fit_history = []

    best_fit_value = 0
    prev_gen_div = 0
    prev_fit_div = 0

    mutation_rate = MUTATION_RATE_0
    mutation_strength = MUTATION_STRENGTH_0
    selection_pressure = SELECTION_PRESSURE_0

    # file names
    timestamp = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
    filename = "data/average_fitness_log_" + timestamp + ".txt"
    filename2 = "data/best_individual_log_" + timestamp + ".txt"

    print("--------------------------------------------------------")
    print("SAVING TO FILES:")
    print(filename)
    print(filename2)

    print("\n      POPULATION SIZE: %4d" % POPULATION_SIZE)
    print("     NUMBER OF TRIALS: %4d" % NUMBER_OF_TRIALS)
    print("      MAX GENERATIONS: %4d\n" % MAX_GENERATIONS)

    print("          CROSSOVER WEIGHT:", CROSSOVER_WEIGHT)
    print("     INITIAL MUTATION RATE:", MUTATION_RATE_0)
    print(" INITIAL MUTATION STRENGTH:", MUTATION_STRENGTH_0)
    print("INITIAL SELECTION PRESSURE:", SELECTION_PRESSURE_0, "\n")
    print("--------------------------------------------------------")
    print("SEEDING POPULATION...")
    start_time = time.time()
    population = generate_random_population(POPULATION_SIZE)
    print("POPULATION SEEDED")
    print("SEEDING TIME: %ds" % (time.time() - start_time))
    print("--------------------------------------------------------")

    # increment generations
    for generation in range(MAX_GENERATIONS):

        print("GENERATION:", generation)
        print("\nASSESSING POPULATION FITNESS...")
        start_time = time.time()
        fits = assess_gen_fits(population)
        print("FITNESS ASSESSED")
        print("ASSESSMENT TIME: %ds\n" % (time.time() - start_time))

        # sort population by fitness
        ranked = rank_fit(population, fits)
        fits.sort()

        # save average generation fitness to file
        f = open(filename, "a")
        avg_fit = np.mean(fits)
        f.write("%d\n" % avg_fit)
        f.close()

        # find average fitness change in past 10 generations
        avg_fit_history.append(avg_fit)
        if len(avg_fit_history) > 10:
            avg_fit_history.pop(0)

        avg_fit_delta

        # genetic diversity
        gen_div = gen_diversity(population)
        gen_delta = gen_div - prev_gen_div
        prev_gen_div = gen_div

        # fitness diversity
        fit_div = math.sqrt(np.var(np.array(fits)))
        fit_delta = fit_div - prev_fit_div
        prev_fit_div = fit_div

        print("  [GENERATION] AVERAGE FITNESS: %d" % avg_fit)
        print("                 GEN DIVERSITY: %f" % gen_div)
        print("                 GEN DELTA: %f" % gen_delta)
        print("                 FIT DIVERSITY: %f" % fit_div)
        print("                 FIT DELTA: %f" % fit_delta)

        if max(fits) > best_fit_value:
            best_individual = ranked[-1]
            best_fit_value = max(fits)
            best_numpy = np.asarray(best_individual)

            f2 = open(filename2, "a")
            writable = np.array2string(best_numpy, separator=",", max_line_width=5000,
                                       formatter={'float_kind': lambda x: "%f" % x})[1:-1]
            f2.write(str(best_fit_value)+"\n"+writable+"\n\n")
            f2.close()

            print("\n  [INDIVIDUAL] BEST FITNESS:", best_fit_value)
            print("               GENOME:", best_individual)

        print("\nSEEDING NEXT GENERATION...")




        print("               MUTATION RATE: %f" % mutation_rate)
        print("           MUTATION STRENGTH: %f" % mutation_strength)
        print("          SELECTION PRESSURE: %f" % selection_pressure)

        fit_dist = gen_probability_distribution(fits, selection_pressure)

        next_generation.clear()
        for i in range(round(POPULATION_SIZE / 2)):
            parent_one = select_parent(ranked, fit_dist)
            parent_two = select_parent(ranked, fit_dist)

            while parent_one == parent_two:
                parent_two = select_parent(ranked, fit_dist)

            child_one, child_two = crossover(parent_one, parent_two)

            mutate(child_one, mutation_rate, mutation_strength)
            mutate(child_one, mutation_rate, mutation_strength)

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


def select_parent(population, fit_dist):
    x = random.uniform(0, 1)

    for index in range(len(population)):
        if x < fit_dist[index]:
            return population[index]


def gen_probability_distribution(fits, selection_pressure):
    pop_size = len(fits)
    weighted_fits = []
    for i in range(pop_size):
        weighted_fits.append((1/(pop_size-i))**(1+selection_pressure))

    total_fitness = sum(weighted_fits)

    fit_percents = [fit/total_fitness for fit in weighted_fits]

    """
    f = open("div_test.txt", "a")
    writable = np.array2string(np.array(fit_percents), separator=",", max_line_width=5000,
                               formatter={'float_kind': lambda x: "%f" % x})[1:-1]
    f.write(writable + "\n")
    f.close()"""

    percent = 0
    fit_dist = []
    for fit in fit_percents:
        percent += fit
        fit_dist.append(percent)

    return fit_dist


def rank_fit(generation, fits):
    return [pair[1] for pair in sorted(zip(fits, generation))]


def assess_gen_fits(generation):
    fit_test = fw(display=False)

    # actual fitness
    return [fit_test.get_fitness(individual, games_max=NUMBER_OF_TRIALS) for individual in generation]

    # random fitness. faster running for testing other features
    # return [random.randint(0, 100) for individual in generation]


def gen_diversity(pop):
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


def mutate(genetic_code, mutation_rate, mutation_strength, max_value=1, min_value=-1):
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
            genetic_code[i] = max(min_value, min(max_value, random.gauss(genetic_code[i], mutation_strength)))


# run main
main()
