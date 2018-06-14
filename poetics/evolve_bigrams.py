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


def line_to_dict(line):
    """
    Determine import features of the given line.

    Accepts tokenized lines, e.g. ['and', 'that', 'which', 'governs', 'me', 'to', 'go', 'about'].
    """
    return {
        'raw_text': line,
        'tokens': nltk.word_tokenize(line.lower()),
        'ends_sentence': line[-1] in {'.', ';', '?', '!'},
    }

import kenlm
path = 'data/lm_csr_5k_nvp_2gram/lm_csr_5k_nvp_2gram.arpa'
path = 'data/lm_csr_64k_nvp_3gram/lm_csr_64k_nvp_3gram.arpa'
klm = kenlm.LanguageModel(path)

TEXT_FILEPATH = 'data/sonnets.txt'
with open(TEXT_FILEPATH, 'r') as f:
    ALL_LINES = f.read().split('\n')
ALL_LINES = [line for line in ALL_LINES if line]
ALL_LINES = [line_to_dict(line) for line in ALL_LINES]

for previous_line, line in zip(ALL_LINES, ALL_LINES[1:]):
    line['starts_sentence'] = previous_line['ends_sentence']

ALL_LINES[0]['starts_sentence'] = True

CORPUSES = nltk.corpus.gutenberg.fileids()
BIGRAM_FREQUENCY = collections.Counter()
for fileid in CORPUSES:
    words = nltk.corpus.gutenberg.words(fileid)
    bigrams = nltk.ngrams([word.lower() for word in words], n=2)
    BIGRAM_FREQUENCY += collections.Counter(bigrams)


def select_random_line(source):
    """Select a random line from a list of all available lines."""
    return random.choice(source)


def replace_random_line(individual, source):
    """Replace a random line in an individual with another randomly chosen one."""
    index = random.randint(0, len(individual) - 1)
    individual[index] = select_random_line(source)
    return individual


def mutate(individual, source):
    """Replace a random number of lines with randomly chosen ones."""
    for i in range(random.randint(0, int(len(individual) / 2.0))):
        replace_random_line(individual, source)
    return individual


def evaluate(individual):
    """Score an individual according to several evaluation methods."""
    methods, weights = zip(*[
        (evaluate_bigram_frequency, 1.0),
        (evaluate_line_endings, 10.0),
        (evaluate_poem_ending, 5.0),
        (evaluate_poem_start, 5.0)
    ])
    score = sum(method(individual) * weight for method, weight in zip(methods, weights))
    return (score,)


def evaluate(individual):
    """Score an individual according to several evaluation methods."""
    poem_as_str = ' '.join([line['raw_text'] for line in individual])
    sentences = nltk.sent_tokenize(poem_as_str)
    score = sum(klm.score(sentence, eos=True, bos=True) for sentence in sentences)
    if len(sentences) < 4:
        score += -1000.0
    return (score,)


def evaluate(individual):
    """Score an individual according to several evaluation methods."""
    poem_as_str = ' '.join([line['raw_text'] for line in individual])
    sentences = nltk.sent_tokenize(poem_as_str)
    score = sum(klm.score(sentence, eos=True, bos=True) for sentence in sentences)
    if len(sentences) < 4:
        score += -1000.0
    return (score,)



def evaluate(individual):
    """Score an individual according to several evaluation methods."""
    poem_as_str = ' '.join([line['raw_text'] for line in individual])
    sentences = nltk.sent_tokenize(poem_as_str)
    score = (-1) * sum(klm.perplexity(sentence) for sentence in sentences)

    if len(sentences) < 4:
        score += -2000.0

    # punish sentences > 3 lines long:
    n_long_sentences = 0
    count = 0
    for line in individual:
        try:
            if not (line[-1] == '.'):
                count += 1
        except KeyError:
            continue
        else:
            count = 0
        if count > 3:
            n_long_sentences += 1
    score += n_long_sentences * (-3000.0)

    raw_lines = [line['raw_text'] for line in individual]
    n_duplicate_lines = len(raw_lines) - len(set(raw_lines))
    score += n_duplicate_lines * (-2000.0)
    return (score,)



def evaluate_bigram_frequency(individual):
    """
    Use the observed bigram frequency to evaluate the reasonability of the line breaks.

    Used to score an individual's fitness.
    """
    # FIXME: This strongly favors poems whose lines begin with 'And'.
    score = 0.0
    for line, next_line in zip(individual, individual[1:]):
        if not line['ends_sentence']:
            bigram = (line['tokens'][-1], next_line['tokens'][0].lower())
            score += math.floor(math.sqrt(math.log(BIGRAM_FREQUENCY[bigram] + 1)))
        elif line['ends_sentence'] and next_line['starts_sentence']:
            score += 2.0
    return score


def evaluate_line_endings(individual):
    """
    Favor a healthy mix of distinct line endings by punishing imbalance.

    Returns a score in the range [-len(individual), 0].
    """
    period_count = sum(line['ends_sentence'] for line in individual)
    comma_count = sum(1 for line in individual if line['tokens'][-1] in {',', ':', '--'})
    other_count = len(individual) - period_count - comma_count
    return min(period_count, comma_count, other_count) \
        - max(period_count, comma_count, other_count)


def evaluate_poem_ending(individual):
    """Favor individuals that end on a full-stop."""
    try:
        return float(individual[-1]['tokens'][-1] == '.')
    except (KeyError, IndexError):
        return 0.0


def evaluate_poem_start(individual):
    """Favor individuals that start with a sentence-starting line."""
    try:
        return individual[0]['starts_sentence']
    except (KeyError, IndexError):
        return 0.0


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
    toolbox.register('mutate', lambda x: (mutate(x, ALL_LINES),))
    toolbox.register('select', tools.selTournament, tournsize=3)

    return toolbox


def evolve_grammatical_poems(toolbox):
    """Let evolution take its course for the given toolbox."""
    population = toolbox.population(n=8000)
    hof = tools.HallOfFame(100)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register('avg', np.mean)
    stats.register('min', np.min)
    stats.register('max', np.max)

    population, logbook = algorithms.eaSimple(
        population=population,
        toolbox=toolbox,
        cxpb=0.50,
        mutpb=0.2,
        ngen=50,
        stats=stats,
        halloffame=hof,
        verbose=True
    )
    return population, logbook, hof


if __name__ == '__main__':
    toolbox = initialize_toolbox()
    population, logbook, hof = evolve_grammatical_poems(toolbox)

    for line in hof[0]:
        print(' '.join(line['tokens']))
