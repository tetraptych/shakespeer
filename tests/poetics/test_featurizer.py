"""Tests for featurizer methods for converting text to dataframes."""
from shakespeer.poetics import featurizer


class TestFeaturizer():
    """Test featurizer methods for converting text to dataframes."""

    @classmethod
    def setup_class(cls):
        """Setup the class by importing raw text data."""
        cls.TEXT_FILEPATH = 'data/sonnets.txt'
        with open(cls.TEXT_FILEPATH, 'r') as f:
            cls.RAW_TEXT = f.read()
        cls.df = featurizer.convert_text_to_dataframe(text=cls.RAW_TEXT)

    def test_convert_text_to_dataframe_yields_correct_columns(self):
        """Test that output dataframe has all the expected columns."""
        for col in ['content', 'rhyme', 'n_words', '0 word', '-1 word']:
            assert col in self.df.columns

    def test_convert_text_to_dataframe_always_yields_valid_rhymes(self):
        """Test that output dataframe has no null values for the rhyme column."""
        null_rhymes = self.df[self.df['rhyme'].isnull()]
        assert null_rhymes.empty
