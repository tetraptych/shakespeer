"""
Genetic algorithms to evolve grammatical poem.

Observation:
    In creating centos, we keep entire lines of existing poems.
    The existing lines are already grammatical internally.
    Therefore we are primarily concerned with grammaticality
    at the seams where two lines meet.
"""
import collections
import math
import random

from deap import algorithms, base, creator, tools

import nltk

import numpy as np


TEXT_FILEPATH = 'data/sonnets.txt'
with open(TEXT_FILEPATH, 'r') as f:
    ALL_LINES = f.read().split('\n')


CORPUSES = nltk.corpus.gutenberg.fileids()
BIGRAM_FREQUENCY = collections.Counter()
for fileid in CORPUSES:
    words = nltk.corpus.gutenberg.words(fileid)
    bigrams = nltk.ngrams(words, n=2)
    BIGRAM_FREQUENCY += collections.Counter(bigrams)


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
    Use the observed bigram frequency to evaluate the reasonability of the line breaks.

    Used to score an individual's fitness.
    """
    # FIXME: This strongly favors poems whose lines begin with 'And'.
    score = 5.0
    for line, next_line in zip(individual, individual[1:]):
        if line and line[-1] not in {'.', ';'}:
            # FIXME: Tokenize outside of this step.
            line_as_words = nltk.word_tokenize(line.lower())
            next_line_as_words = nltk.word_tokenize(next_line.lower())
            if line_as_words and next_line_as_words:
                bigram_upper = (line_as_words[-1], next_line_as_words[0])
                bigram_lower = (line_as_words[-1], next_line_as_words[0].lower())
                score_upper = BIGRAM_FREQUENCY[bigram_upper]
                score_lower = BIGRAM_FREQUENCY[bigram_lower]
                score_to_add = max(score_upper, score_lower)
                if score_to_add > 0:
                    score += math.log(score_to_add)

    return (score,)


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


def evolve_grammatical_poems(toolbox):
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
    population, logbook, hof = evolve_grammatical_poems(toolbox)
    print(hof[0])
