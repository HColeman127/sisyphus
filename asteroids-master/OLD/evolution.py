import random
import numpy as np
import time
import math
import threading
from FitnessWrapper import FitnessWrapper as fw


# CONSTANTS
POPULATION_SIZE = 100
NUMBER_OF_TRIALS = 10
MAX_STEPS = 200
MAX_GENERATIONS = 1000

CARRY_OVER = 0
CROSSOVER_WEIGHT = 0.25
MUTATION_RATE_0 = 0.10
MUTATION_STRENGTH_0 = 0.2
SELECTION_PRESSURE_0 = 1.3



def main():
    population = []
    next_generation = []
    best_individual = []
    avg_fit_history = []
    load_from_file = False
    save_at_gens = [] # ex: [1,5,6] - this will save at generations 1, 5 and 6
    file_loc_load = "???"
    file_loc_save = "???"

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

    print("\n        GENOME LENGTH: %4d" % fw.GENOME_LENGTH)
    print("      POPULATION SIZE: %4d" % POPULATION_SIZE)
    print("     NUMBER OF TRIALS: %4d" % NUMBER_OF_TRIALS)
    print("       MAX GAME STEPS: %4d" % MAX_STEPS)
    print("      MAX GENERATIONS: %4d\n" % MAX_GENERATIONS)

    print("                CARRY OVER:", CARRY_OVER)
    print("          CROSSOVER WEIGHT:", CROSSOVER_WEIGHT)
    print("     INITIAL MUTATION RATE:", MUTATION_RATE_0)
    print(" INITIAL MUTATION STRENGTH:", MUTATION_STRENGTH_0)
    print("INITIAL SELECTION PRESSURE:", SELECTION_PRESSURE_0, "\n")
    print("--------------------------------------------------------")
    print("SEEDING POPULATION...")

    if load_from_file:
        start_time = time.time()
        population = load_from_file(file_loc_load + ".txt")
    else:
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
        f.write("%f\n" % avg_fit)
        f.close()

        # find average fitness change in past 10 generations
        avg_fit_history.append(avg_fit)
        if len(avg_fit_history) > 10:
            avg_fit_history.pop(0)

        avg_fit_delta = (avg_fit_history[-1]-avg_fit_history[0])/len(avg_fit_history)

        # genetic diversity
        gen_div = gen_diversity(population)
        gen_delta = gen_div - prev_gen_div
        prev_gen_div = gen_div

        # fitness diversity
        fit_div = math.sqrt(np.var(np.array(fits)))
        fit_delta = fit_div - prev_fit_div
        prev_fit_div = fit_div

        print("  [GENERATION] AVERAGE FITNESS: %f" % avg_fit)
        print("               AVG FIT DELTA: %f\n" % avg_fit_delta)
        print("                 GEN DIVERSITY: %f" % gen_div)
        print("                 GEN DELTA: %f" % gen_delta)
        print("                 FIT DIVERSITY: %f" % fit_div)
        print("                 FIT DELTA: %f" % fit_delta)

        gen_best_individual = ranked[-1]
        gen_best_value = max(fits)

        print("\n  [INDIVIDUAL] BEST FITNESS:", gen_best_value)
        print("               GENOME:", gen_best_individual)


        if gen_best_value > best_fit_value:
            best_individual = gen_best_individual
            best_fit_value = gen_best_value
            best_numpy = np.array(best_individual)

            f2 = open(filename2, "a")
            #writable = np.array2string(best_numpy, separator=",", max_line_width=5000)
            f2.write(str(best_fit_value)+"\n"+str(best_individual)+"\n\n")
            f2.close()

            print("\n      ALL TIME BEST FITNESS:", best_fit_value)
            print("               GENOME:", best_individual)

        if generation in save_at_gens:
            timestamp = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
            save_population(population, file_loc_save + timestamp + ".txt")


        print("\nSEEDING NEXT GENERATION...")

        print("               MUTATION RATE: %f" % mutation_rate)
        print("           MUTATION STRENGTH: %f" % mutation_strength)
        print("          SELECTION PRESSURE: %f" % selection_pressure)

        fit_dist = gen_probability_distribution(fits, selection_pressure)

        if CARRY_OVER > 0:
            next_generation = ranked[-CARRY_OVER:]
        else:
            next_generation = []

        for i in range((POPULATION_SIZE-CARRY_OVER)//2):
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

        print("POPULATION SIZE:", len(population))
        print("NEXT GENERATION SEEDED")
        print("--------------------------------------------------------")
    # exit loop at generation max

    print("CLOSING")
    print(best_individual)

# =================================================================
# =    HELPER METHODS                                             =
# =================================================================


# reads and loads the popoulation from the file at filedest.txt

def load_population(filedest):

    print("LOADING FROM FILE AT " + filedest +"...")
    with open(filedest, "r") as ins:
        gen = []
        for line in ins:
            line.strip("\n")
            print("line", line)
            gen.append(line)

    return gen

# saves the inputted population to a file created at filedest.txt
def save_population(generation, filedest):

    #print("Saving Generation at", filedest, ".txt...")
    #print("Generation: ", generation)
    f = open(filedest, "a")
    for individual in generation:
        f.write(str(individual) + "\n")
    f.close()



def select_parent(population, fit_dist):
    x = random.uniform(0, 1)

    for index in range(len(population)):
        if x < fit_dist[index]:
            return population[index]


def gen_probability_distribution(fits, selection_pressure):
    pop_size = len(fits)
    weighted_fits = []
    for i in range(pop_size):
        weighted_fits.append((1/(pop_size-i+1))**selection_pressure)

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

    size = len(generation)
    print(end="|")
    for _ in range(size):
        print(end="-")
    print(end="|\n|")

    fits = []
    seed = random.random()

    for i in range(size):

        fits.append(fit_test.get_fitness(generation[i], games_max=NUMBER_OF_TRIALS,
                                                     step_max=MAX_STEPS, random_seed=seed))
        print("#", end="", flush=True)


    print("|")


    return fits


def gen_diversity(pop):
    return np.average([math.sqrt(np.var(np.array(pop)[:, i])) for i in range(len(pop[0]))])


def generate_random_population(size=100):
    return [generate_random_individual(length=fw.GENOME_LENGTH) for _ in range(size)]


def generate_random_individual(min_value=-1, max_value=1, length=fw.GENOME_LENGTH):
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
            new_value = max(min_value, min(max_value, random.gauss(genetic_code[i], mutation_strength)))
            #new_value = random.uniform(-1, 1)
            genetic_code[i] = new_value


# run main
main()
