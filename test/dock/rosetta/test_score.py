import unittest
import os
import pandas as pd

from pepkit.dock.rosetta.score import read_and_convert, extract_score, get_optimal_clx
from pepkit.examples import rosetta_data

TEST_DIR = rosetta_data.get_refinement_path()
TEST_SCORE = os.path.join(TEST_DIR, "complex_1", "docking_scores.sc")


class TestRosettaScoreUtils(unittest.TestCase):
    def test_read_and_convert(self):
        df = read_and_convert(TEST_SCORE)
        self.assertIsInstance(df, pd.DataFrame)
        # Check basic structure: has at least description column and is non-empty
        self.assertIn("description", df.columns)
        self.assertFalse(df.empty)

    def test_extract_score(self):
        df_all = extract_score(TEST_DIR)
        self.assertIsInstance(df_all, pd.DataFrame)
        # Should have an 'id' column and 'description'
        self.assertIn("id", df_all.columns)
        self.assertIn("description", df_all.columns)
        # Should have at least as many rows as the number of input files
        self.assertGreaterEqual(df_all.shape[0], 1)
        # Check that id is correct (should match folder names like 'complex_1')
        self.assertIn("complex_1", df_all["id"].unique())

    def test_get_optimal_clx(self):
        df = read_and_convert(TEST_SCORE)
        opt = get_optimal_clx(df)
        # Should return a string from the 'description' column
        self.assertIsInstance(opt, str)
        self.assertIn(opt, df["description"].values)


if __name__ == "__main__":
    unittest.main()
