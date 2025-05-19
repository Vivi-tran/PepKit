import unittest
import pandas as pd
from typing import List, Dict, Any

from pepkit.chem.descriptor import Descriptor


class TestDescriptorPeptides(unittest.TestCase):
    def setUp(self):
        self.sample_df = pd.DataFrame(
            [
                {"id": "pep1", "peptide_sequence": "ACDE"},
                {"id": "pep2", "peptide_sequence": "FGHI"},
            ]
        )
        self.descriptor = Descriptor(engine="peptides")

    def test_calculate_dataframe(self):
        out = self.descriptor.calculate(self.sample_df, n_jobs=1)
        # Expect same number of rows
        self.assertEqual(len(out), len(self.sample_df))
        # Expect id and sequence columns preserved
        self.assertTrue(set(["id", "peptide_sequence"]).issubset(out.columns))

    def test_calculate_list(self):
        records: List[Dict[str, Any]] = self.sample_df.to_dict(orient="records")
        out = self.descriptor.calculate(records, n_jobs=1)
        self.assertIsInstance(out, list)
        self.assertEqual(len(out), len(records))
        self.assertIn("id", out[0])

    def test_missing_keys(self):
        bad_records = [{"peptide_sequence": "AAAA"}]  # missing id
        with self.assertRaises(KeyError):
            self.descriptor.calculate(bad_records, n_jobs=1)


class TestDescriptorRDKit(unittest.TestCase):
    def setUp(self):
        self.sample_df = pd.DataFrame(
            [
                {"id": "mol1", "smiles": "CCO"},
                {"id": "mol2", "smiles": "CC(=O)O"},
            ]
        )
        self.descriptor = Descriptor(engine="rdkit")

    def test_calculate_dataframe(self):
        out = self.descriptor.calculate(self.sample_df, n_jobs=1)
        self.assertEqual(len(out), len(self.sample_df))
        self.assertTrue(set(["id", "smiles"]).issubset(out.columns))

    def test_invalid_smiles(self):
        bad_records = [{"id": "bad", "smiles": "not_a_smiles"}]
        with self.assertRaises(ValueError):
            self.descriptor.calculate(bad_records, n_jobs=1)

    def test_parallel_vs_serial(self):
        # Compare outputs with and without joblib parallelism
        df = pd.concat([self.sample_df] * 5, ignore_index=True)
        serial = self.descriptor.calculate(df, n_jobs=1)
        parallel = self.descriptor.calculate(df, n_jobs=2)
        pd.testing.assert_frame_equal(serial, parallel)


if __name__ == "__main__":
    unittest.main()
