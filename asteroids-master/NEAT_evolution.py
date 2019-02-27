from NEAT_Individual import *
import time
import copy
import numpy as np

try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle


# individuals
INPUT_SIZE = 8
OUTPUT_SIZE = 2

# population
POPULATION_SIZE = 100
NUMBER_OF_TRIALS = 10
MAX_STEPS = 5000
MAX_GENERATIONS = 1000

# evolutionary
SURVIVOR_PROPORTION = 0.50
RE_EXPRESSION_CHANCE = 0.25

# mutation
MUTATE_ALL_WEIGHTS_CHANCE = 0.80
MUTATE_WEIGHT_CHANCE = 0.90
MUTATE_WEIGHT_STRENGTH = 0.10

MUTATE_NODE_CHANCE = 0.10
MUTATE_CONNECTION_CHANCE = 0.30

# speciation
compatibility_threshold = 0.17

# global variables (sue me)
node_number = INPUT_SIZE+OUTPUT_SIZE+1
#connection_number = INPUT_SIZE*OUTPUT_SIZE+1
connection_number = 0

# filenames
timestamp = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
filename = "data/average_fitness_log_" + timestamp + ".txt"
filename2 = "data/best_individual_log_" + timestamp + ".txt"

pickle_file = "data/best_individuals_" + timestamp + ".dat"


# loading bars
spacer = "_"
bit = "/"
inds = 2


def main():
    # global values
    global node_number
    global connection_number
    global best_individuals

    # pickle stuff
    best_individuals = []

    print("-"*60)
    print("SAVING TO FILES:")
    print(filename)
    print(pickle_file)
    print()

    # generate initial population
    population = gen_rand_pop(POPULATION_SIZE)

    for gen_number in range(MAX_GENERATIONS):
        print("GENERATION:", gen_number, "\n")
        raw_fits = assess_pop_fits(population)
        adj_fits = calc_pop_adj_fits(population)
        sorted_pop = sort_pop(population)

        fit_stats(adj_fits, sorted_pop)

        # prep for next generation
        print("-"*40)
        culled_pop = cull_population(sorted_pop)
        species_list = speciate_pop(culled_pop)
        allocations = allocate_offspring(species_list)

        # save best individual to file
        best_individuals = []
        for species in species_list:
            best_individuals.append(copy.deepcopy(species[-1]))

        file_pi = open(pickle_file, 'wb')
        pickle.dump(best_individuals, file_pi)
        #print("PICKLED BEST INDIVIDUALS")


        # creates the next generation
        population = create_next_gen(species_list, allocations)

        print("COMPATIBILITY THRESHOLD:", compatibility_threshold)
        print("  OFFSPRING ALLOCATIONS:", allocations)
        print("   NEXT GENERATION SIZE:", len(population))
        print("="*80+"")




def gen_rand_pop(size: int) -> list:
    print(end="SEEDING POPULATION...")
    population = [Individual(input_size=INPUT_SIZE, output_size=OUTPUT_SIZE) for _ in range(size)]
    print("DONE")
    print("="*80)
    return population


def assess_fit(target: Individual) -> None:
    target.assess_fitness(max_trials=NUMBER_OF_TRIALS,  max_steps=MAX_STEPS, display=False)


def assess_pop_fits(population: list) -> list:
    start_time = time.time()
    loading("ASSESSING POPULATION FITNESS", len(population))

    for i in range(len(population)):
        assess_fit(population[i])
        blip(i)

    end_load(start_time)

    fits = [individual.fitness for individual in population]
    return fits


def get_compatibility_distance(ind_one: Individual, ind_two: Individual) -> float:

    excess_gene_weight = 1
    disjoint_gene_weight = 1
    weight_diff_weight = 0.4

    ind_one_connections = ind_one.genome.get_connection_ids()
    ind_two_connections = ind_two.genome.get_connection_ids()

    # --- deal with edge case of null individual
    if len(ind_one_connections) == 0 and len(ind_two_connections) == 0:
        return 0
    if len(ind_one_connections) == 0 and len(ind_two_connections) != 0:
        return len(ind_two_connections) * excess_gene_weight
    if len(ind_one_connections) != 0 and len(ind_two_connections) == 0:
        return len(ind_one_connections) * excess_gene_weight

    disjoints = 0

    # -- calc num of disjoints and excesses
    if len(ind_one_connections) == 0: ind_one_connections.append(0)
    if len(ind_two_connections) == 0: ind_two_connections.append(0)

    max_val = max(max(ind_one_connections), max(ind_two_connections))
    min_val = min(max(ind_one_connections), max(ind_two_connections))

    for count in range(min_val+1):
        if (count in ind_one_connections) ^ (count in ind_two_connections):
                disjoints += 1


    ran = range(min_val+1, max_val+1)
    one = len(set(ran).intersection(ind_one_connections))
    two = len(set(ran).intersection(ind_two_connections))

    excesses = max(one, two)
    # -- end

    # -- calc avg. weight differences of matching connections
    matching = set(ind_one_connections).intersection(ind_two_connections)
    number = len(matching)
    sum = 0

    for num in matching:
        weight1 = ind_one.genome.connections[num].weight
        weight2 = ind_two.genome.connections[num].weight
        difference = abs(weight1 - weight2)
        sum += difference

    average = sum/max(1, number)

    large_genome_size = max(len(ind_one_connections), len(ind_two_connections)) # N is the size of the larger genome

    compatibility_distance = (excess_gene_weight*excesses)/large_genome_size + \
                             (disjoint_gene_weight*disjoints)/large_genome_size + weight_diff_weight * average

    #print("Comp Dist: ", compatibility_distance)
    return compatibility_distance


def calc_adj_fit(target: Individual, population: list) -> float:
    global compatibility_threshold
    species_size = 0
    comp_dists = []

    # dynamically calculate comp threshold

    for individual in population:
        comp_dist = get_compatibility_distance(target, individual)
        comp_dists.append(comp_dist)

    for dist in comp_dists:
        if dist <= compatibility_threshold:
            species_size += 1

    target.adj_fitness = target.fitness/species_size

    return sum(comp_dists)/len(comp_dists)


def calc_pop_adj_fits(population: list) -> list:
    global compatibility_threshold
    start_time = time.time()
    loading("CALCULATING ADJUSTED FITNESSES", len(population))
    comp_dists = []

    for i in range(len(population)):
        comp_dists.append(calc_adj_fit(population[i], population))
        blip(i)

    adj_fits = [individual.adj_fitness for individual in population]

    compatibility_threshold = sum(comp_dists)/len(comp_dists)

    end_load(start_time)
    print("-"*40+"\n")
    return adj_fits


def sort_pop(population: list) -> list:
    #print(end="          SORTING POPULATION...", flush=True)
    fits = [individual.adj_fitness for individual in population]
    sorted_zip = sorted(zip(fits, range(POPULATION_SIZE), population))
    sorted_pop = [ind[2] for ind in sorted_zip]
    #print("DONE")
    return sorted_pop


def cull_population(population: list) -> list:
    #print(end="    CULLING POPULATION [" + str(SURVIVOR_PROPORTION) + "]...", flush=True)
    culled_pop = population[round(-SURVIVOR_PROPORTION*POPULATION_SIZE):]
    #print("DONE")
    return culled_pop


def speciate_pop(population: list) -> list:
    #print(end="       SPECIATING POPULATION...", flush=True)
    global species_number
    species_list = []
    species_number = 0

    for i in range(len(population)):
        target = population[i]
        target.species = -1
        for species in species_list:
            if get_compatibility_distance(target, species[0]) <= compatibility_threshold:
                target.species = species[0].species
                species.append(target)
                break
        if target.species == -1:
            target.species = species_number
            species_list.append([target])
            species_number += 1

    #print("DONE")
    return species_list


def allocate_offspring(species_list: list) -> list:
    #print(end="ALLOCATING SPECIES OFFSPRING...", flush=True)

    allocations = []
    for species in species_list:
        allocations.append(0)
        for individual in species:
            allocations[-1] += individual.adj_fitness
    total = sum(allocations)

    for i in range(len(allocations)):
        allocations[i] = round(allocations[i]*POPULATION_SIZE/max(0.0000001, total))

    #print("DONE")
    return allocations


def create_next_gen(species_list: list, allocations: list) -> list:
    #print(end="    CREATING NEXT GENERATION...", flush=True)
    next_gen = []

    # i is the species number
    for i in range(len(species_list)):
        # create the selecition distribution for this species
        dist = create_selection_dist(species_list[i])

        # create children a number of times given in the allocations list
        for child_count in range(allocations[i]):

            # select first parent
            value = random.uniform(0, 1)
            k = 0
            while value > dist[k]:
                k += 1
            parent1 = species_list[i][k]

            # select second parent
            value = random.uniform(0, 1)
            k = 0
            while value > dist[k]:
                k += 1
            parent2 = species_list[i][k]

            # ensure parent1 is higher fitness
            if parent2.adj_fitness > parent1.adj_fitness:
                parent1, parent2 = parent2, parent1

            # create child and add to next generation list
            child = crossover(parent1, parent2)

            # mutate child
            if random.uniform(0, 1) < MUTATE_ALL_WEIGHTS_CHANCE:
                child.mutate_weights(MUTATE_WEIGHT_CHANCE, MUTATE_WEIGHT_STRENGTH)

            if random.uniform(0, 1) < MUTATE_NODE_CHANCE:
                mutate_node(child)

            if random.uniform(0, 1) < MUTATE_CONNECTION_CHANCE:
                mutate_connection(child)

            # add child to list
            next_gen.append(child)

    #print("DONE\n"+"-"*40+"\n")
    # return new population
    return next_gen


def create_selection_dist(group: list) -> list:
    dist = []
    for individual in group:
        dist.append(individual.adj_fitness)

    total = sum(dist)
    running_sum = 0
    for i in range(len(dist)):
        running_sum += dist[i]
        dist[i] = running_sum/max(0.0000001, total)

    return dist


def crossover(high: Individual, low: Individual) -> Individual:
    child = copy.deepcopy(high)

    for con_id in child.genome.get_connection_ids():

        if con_id in low.genome.get_connection_ids():

            isExpressed = True

            if not child.genome.connections[con_id].expressed:
                rand = random.uniform(0, 1)
                if rand >= RE_EXPRESSION_CHANCE:
                    isExpressed = False

            rand = random.randint(0, 1)
            if rand == 0:
                child.genome.connections[con_id].weight = low.genome.connections[con_id].weight

            child.genome.connections[con_id].expressed = isExpressed

    return child


def mutate_node(individual: Individual) -> None:
    global node_number
    global connection_number
    if individual.mutate_node(node_number, connection_number):
        node_number += 1
        connection_number += 2
    else:
        pass


def mutate_connection(individual: Individual) -> None:
    global connection_number
    if individual.mutate_connection(connection_number):
        connection_number += 1
    else:
        pass


# formatting shit -----------------------------------------
def blip(value: int) -> None:
    if value % inds == inds - 1:
        print(end=bit, flush=True)


def loading(title: str, length: int) -> None:
    top = " "+title
    top += spacer * (length // inds - len(title))
    top += "\n|"
    print(end=top)


def end_load(start_time: float) -> None:
    print("| %ds\n" % (time.time() - start_time))


def fit_stats(fit_list: list, sorted_pop: list) ->None:
    avg_adj_fit = sum(fit_list) / len(fit_list)
    print("AVG ADJ FITNESS:", avg_adj_fit, "\n")
    f = open(filename, "a")
    f.write("%f\n" % avg_adj_fit)
    f.close()

    print("BEST FITNESS:", sorted_pop[-1].adj_fitness)
    print()


# run main
if __name__ == '__main__':
    start_time = time.time()
    main()
    print("\n\nTOTAL EVALUATION TIME:", time.time()-start_time)
