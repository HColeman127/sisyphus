from FitnessWrapper_small import FitnessWrapper as fw
import random
import numpy as np
import time

fit = fw(display=True)

scoop = [0.7122270812431213, 1, -0.5152562318261517, 0.8222036658014363, 0.9295837104964634, 0.9565718928103633, -0.20577908294799666, -0.4563585869129153, 0.13964257273914138, 0.26547947919898807, -0.6763363526774424, -0.71196347985002, -0.7399739071233986, 0.7728358749390807, -0.02243543177847075, -0.28183390870402203, -0.23435732542631266, -0.8060119633029916, -0.0820913081826791, 0.1535423979661938, -0.18565794448385448, 0.8166687496462817, -0.6605832243430492, -0.7373024701349138, 0.5033566201743112]


filename = "logs/mean_log_" + time.strftime("%Y-%m-%d-%H%M%S", time.localtime()) + ".txt"


def main():

    print(fit.get_fitness(scoop, games_max=10, step_max=500, random_seed=random.random()))


def random_boye():
    return [random.uniform(-1, 1) for _ in range(fw.GENOME_LENGTH)]

start_time = time.time()
main()
print("\n\nRUNTIME: %.2f" % (time.time()-start_time))
