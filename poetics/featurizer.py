"""Methods to convert raw text into a format usable by Poem objects."""
import string

import pandas as pd

import pronouncing

import unidecode


def convert_text_to_dataframe(text):
    """
    Convert raw text to a DataFrame object.

    The output dataframe has the following columns:
        - 'content': The cleaned text for each line.
        - 'rhyme': The rhyme class for each line.
        - 'n_words': The number of words in each line.
        - '0 word': The first word of the line.
        - '-1 word': The last word of the line.
    """
    lines = _convert_text_to_lines(text)
    df = pd.DataFrame(
        data=lines,
        columns=['content']
    )
    df['rhyme'] = df['content'].apply(_determine_rhyme_from_line)
    df = df[df['rhyme'].notnull()]
    df['n_words'] = df['content'].apply(lambda line: len(line.split()))
    df = _add_nth_word_column(df, n=0)
    df = _add_nth_word_column(df, n=-1)
    return df


def _convert_text_to_lines(text):
    """Convert raw text to a list of lines."""
    invalid_lines = set(('', ' ', '.', ','))
    lines = text.strip().replace(':', ':\n').split('\n')
    lines = [x.strip() for x in lines if x not in invalid_lines]
    lines = [unidecode.unidecode(line) for line in lines if line[-1] != ':']

    translator = str.maketrans(
        string.ascii_uppercase,
        string.ascii_lowercase,
        string.punctuation + '0123456789'
    )
    lines = [
        line.translate(translator).strip()
        for line in lines
    ]
    return [x for x in lines if x not in invalid_lines]


def _determine_rhyme_from_line(line):
    """
    Return the rhyming part of a string.

    If no rhyming part is detected, return None.
    """
    end_word = line.split()[-1]
    end_phone = pronouncing.phones_for_word(end_word)

    if end_phone != []:
        end_rhyme = pronouncing.rhyming_part(end_phone[0])
    else:
        end_rhyme = None

    return end_rhyme


def _add_nth_word_column(df, n, text_column='content'):
    """Add a column representing the n-th word of each line."""
    df['{n} word'.format(n=n)] = df[text_column].apply(lambda line: line.split()[n])
    return df
