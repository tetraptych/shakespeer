"""Genetic algorithms to evolve Sonnet 129."""
import random

import numpy as np

from deap import base, creator, tools, algorithms


TEXT_FILEPATH = 'data/sonnets.txt'
with open(TEXT_FILEPATH, 'r') as f:
    ALL_LINES = f.read().split('\n')

SONNET_129 = ALL_LINES[393:393 + 14]


def select_random_line(source):
    """Select a random line from a list of all available lines."""
    return random.choice(source)


def replace_random_line(individual, source):
    """Replace a random line in an individual with another randomly chosen one."""
    index = random.randint(0, len(individual) - 1)
    individual[index] = select_random_line(source)
    return individual


def evaluate(individual):
    """
    Measure the number of times the same line from Sonnet 129 appears in the poem.

    Used to score an individual's fitness.
    """
    return sum(line == target for line, target in zip(individual, SONNET_129)),


def initialize_toolbox():
    """Register methods used to mate, mutate, and evaluate poems."""
    creator.create('FitnessMax', base.Fitness, weights=(1.0,))
    creator.create('Individual', list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register('random_line', select_random_line, ALL_LINES)
    toolbox.register('individual', tools.initRepeat, creator.Individual, toolbox.random_line, n=14)
    toolbox.register('population', tools.initRepeat, list, toolbox.individual)

    toolbox.register('evaluate', evaluate)
    toolbox.register('mate', tools.cxOnePoint)
    toolbox.register('mutate', lambda x: (replace_random_line(x, ALL_LINES),))
    toolbox.register('select', tools.selTournament, tournsize=3)

    return toolbox


def evolve_sonnet_129(toolbox):
    """Let evolution take its course for the given toolbox."""
    population = toolbox.population(n=5000)
    hof = tools.HallOfFame(10)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register('avg', np.mean)
    stats.register('min', np.min)
    stats.register('max', np.max)

    population, logbook = algorithms.eaSimple(
        population=population,
        toolbox=toolbox,
        cxpb=0.5,
        mutpb=0.2,
        ngen=30,
        stats=stats,
        halloffame=hof,
        verbose=True
    )
    return population, logbook, hof


if __name__ == '__main__':
    toolbox = initialize_toolbox()
    population, logbook, hof = evolve_sonnet_129(toolbox)
    print(hof[0])
