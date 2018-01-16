"""Tests for the Poem class and methods contained therein."""
from shakespeer.poetics import featurizer
from shakespeer.poetics import poem


class TestPoem():
    """Test methods for generating poems from source text."""

    @classmethod
    def setup_class(cls):
        """Setup the class by importing raw text data into a DataFrame."""
        cls.TEXT_FILEPATH = 'data/sonnets.txt'
        with open(cls.TEXT_FILEPATH, 'r') as f:
            cls.RAW_TEXT = f.read()
        cls.source_df = featurizer.convert_text_to_dataframe(text=cls.RAW_TEXT)

    def test_init(self):
        """Test that all attributes are correctly initialized."""
        sonnet = poem.Poem(scheme=poem.PETRARCHAN_SONNET)
        expected_inverse_scheme = {
            'A': [0, 3, 4, 7],
            'B': [1, 2, 5, 6],
            'C': [8, 11],
            'D': [9, 12],
            'E': [10, 13]
        }
        assert sonnet.inverse_scheme == expected_inverse_scheme
        assert sonnet.endings_to_rhymes == {}
        assert sonnet.available_lines_by_ending == {}
        assert len(sonnet.lines) == 14

    def test_fill(self):
        """Test that a poem can be filled with lines from the source dataframe."""
        sonnet = poem.Poem(scheme=poem.PETRARCHAN_SONNET)
        sonnet.fill(source=self.source_df)
