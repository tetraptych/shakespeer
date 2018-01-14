"""Class to build poems line-by-line."""
import collections

ELIZABETHAN_SONNET = (
    ['A', 'B'] * 2 +
    ['C', 'D'] * 2 +
    ['E', 'F'] * 2 +
    ['G'] * 2
)
PETRARCHAN_SONNET = (
    ['A', 'B', 'B', 'A'] * 2 +
    ['C', 'D', 'E', 'C', 'D', 'E']

)
BRIAN_SONNET = (
    ['A', 'B', 'C', 'B', 'A', 'C', 'B', 'C', 'A'] +
    ['D', 'E', 'A', 'D', 'E']
)


class Poem(object):
    """
    A poem object.

    Attributes
    ----------
    scheme: list
        A list of endings by line number.
        Ex.: ['A', 'B', 'A', 'C']

    inverse_scheme: dict
        A mapping from endings to lines with that ending.
        Populated via `scheme` on initialization.
        Ex.: {'A': [0, 2], 'B': [1], 'C': [3]}

    endings_to_rhymes: dict
        A mapping from abstract endings to concrete rhymes.
        Ex.: {'A': 'OW1', 'B': 'EH2 T', C: 'AH1 S'}
    """

    def __init__(self, scheme):
        """Initialize a poem with a given rhyme scheme."""
        self.scheme = scheme
        self.inverse_scheme = self._invert_list_to_dictionary(scheme)
        self.endings_to_rhymes = {}
        self.available_lines_by_ending = {}
        self.lines = [''] * len(scheme)

    @staticmethod
    def _invert_list_to_dictionary(iterable):
        """
        Convert a list to a mapping {value: [indices for that value]}.

        >>>_invert_list_to_dictionary([3, 2, 2, 1])
        >>> {3: [0], 2: [1, 2], 1: [3]}
        """
        inverted = collections.defaultdict(list)
        for idx, value in enumerate(iterable):
            inverted[value].append(idx)

        return inverted

    def _pick_rhyme_for_ending(self, ending, source):
        """
        Pick a rhyme for a single ending in the rhyme scheme.

        Chooses a random unseen rhyme.
        """
        rhyme = source['rhyme'].sample(1).iloc[0]
        while rhyme in self.endings_to_rhymes.values():
            rhyme = source['rhyme'].sample(1).iloc[0]

        self.endings_to_rhymes[ending] = rhyme
        self.available_lines_by_ending[ending] = source[source['rhyme'] == rhyme]
        return rhyme

    def _pick_rhymes_for_all_endings(self, source):
        """Determine rhymes for all endings in the rhyme scheme."""
        for ending in self.inverse_scheme:
            self._pick_rhyme_for_ending(ending, source)
        return self.endings_to_rhymes

    def _fill_line(self, index):
        """
        Choose a random line matching the chosen rhyme scheme.

        Requires that the rhyme class for the line's ending has been chosen,
        e.g. by a previous call to `_pick_rhymes_for_all_endings`.
        """
        ending = self.scheme[index]
        text = self.available_lines_by_ending[ending]['content'].sample(1).iloc[0]
        self.lines[index] = text
        return text

    def _fill_lines(self):
        """Fill all lines with text."""
        for index in range(len(self.lines)):
            self._fill_line(index)

    def fill(self, source):
        """Choose rhymes, then fill all lines with text."""
        self._pick_rhymes_for_all_endings(source)
        self._fill_lines()
        return self

    def __str__(self):
        """Represent the poem as a string."""
        return '\n'.join([line for line in self.lines if line])
