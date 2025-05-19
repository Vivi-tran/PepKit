import unittest
import pandas as pd
import logging

import pepkit.chem.standardize as mod
from pepkit.chem.standardize import Standardizer, _CANONICAL_AA


class TestStandardizer(unittest.TestCase):
    def setUp(self):
        # Patch fasta_to_smiles to return a predictable SMILES
        self._orig_f2s = mod.fasta_to_smiles
        mod.fasta_to_smiles = lambda seq: seq + "_SMI"
        # Patch add_charge_by_pH to be predictable
        self._orig_charge = Standardizer.add_charge_by_pH
        Standardizer.add_charge_by_pH = staticmethod(lambda smi, pH: f"{smi}_CHG{pH}")
        # Create a Standardizer instance with both flags enabled
        self.std = Standardizer(remove_non_canonical=True, charge_by_pH=True, pH=6.5)

    def tearDown(self):
        # Restore original fasta_to_smiles and add_charge_by_pH
        mod.fasta_to_smiles = self._orig_f2s
        Standardizer.add_charge_by_pH = self._orig_charge

    def test_is_canonical_sequence_valid(self):
        seq = "".join(_CANONICAL_AA)
        self.assertTrue(Standardizer.is_canonical_sequence(seq))

    def test_is_canonical_sequence_invalid(self):
        self.assertFalse(Standardizer.is_canonical_sequence("ABCZ"))

    def test_is_canonical_sequence_type_error(self):
        with self.assertRaises(TypeError):
            Standardizer.is_canonical_sequence(123)

    def test_process_fasta_canonical_no_charge(self):
        # No charge step
        orig_charge = Standardizer.add_charge_by_pH
        Standardizer.add_charge_by_pH = staticmethod(lambda smi, pH: smi)  # no charge
        try:
            result = Standardizer.process_fasta(
                "ACD", remove_non_canonical=True, charge_by_pH=False
            )
            self.assertEqual(result, "ACD_SMI")
        finally:
            Standardizer.add_charge_by_pH = orig_charge

    def test_process_fasta_noncanonical_filtered(self):
        result = Standardizer.process_fasta(
            "AB", remove_non_canonical=True, charge_by_pH=False
        )
        self.assertIsNone(result)

    def test_process_fasta_charge(self):
        # Should add _CHG7.0
        result = Standardizer.process_fasta(
            "ACD", remove_non_canonical=False, charge_by_pH=True, pH=7.0
        )
        self.assertEqual(result, "ACD_SMI_CHG7.0")

    def test_dict_process(self):
        data = [{"seq": "AAA"}, {"seq": "BXD"}]
        processed = Standardizer.dict_process(
            data, fasta_key="seq", remove_non_canonical=True, charge_by_pH=False
        )
        self.assertEqual(processed[0]["smiles"], "AAA_SMI")
        self.assertIsNone(processed[1]["smiles"])

    def test_process_list_fasta(self):
        seqs = ["AAA", "ZZZ"]
        results = self.std.process_list_fasta(seqs, n_jobs=1)
        self.assertEqual(results[0], "AAA_SMI_CHG6.5")
        self.assertIsNone(results[1])

    def test_data_process_list_dict(self):
        data = [{"fasta": "AC"}, {"fasta": "BZ"}]
        out = self.std.data_process(data, fasta_key="fasta", n_jobs=1)
        self.assertIsInstance(out, list)
        self.assertEqual(out[0]["smiles"], "AC_SMI_CHG6.5")
        self.assertIsNone(out[1]["smiles"])

    def test_data_process_dataframe(self):
        df = pd.DataFrame({"fasta": ["A", "Z"]})
        out_df = self.std.data_process(df, fasta_key="fasta", n_jobs=1)
        self.assertIsInstance(out_df, pd.DataFrame)
        self.assertIn("smiles", out_df.columns)
        self.assertEqual(out_df.loc[0, "smiles"], "A_SMI_CHG6.5")
        self.assertIsNone(out_df.loc[1, "smiles"])

    def test_example_usage_list_and_dataframe(self):
        std = Standardizer(remove_non_canonical=True, charge_by_pH=True, pH=7.0)
        seqs = ["ACDEFGHIK", "XYZ"]
        # process_list_fasta
        list_res = std.process_list_fasta(seqs, n_jobs=1)
        self.assertEqual(list_res, ["ACDEFGHIK_SMI_CHG7.0", None])
        # data_process on DataFrame
        df = pd.DataFrame({"id": [1, 2], "fasta": seqs})
        df_res = std.data_process(df, fasta_key="fasta", n_jobs=1)
        self.assertIsInstance(df_res, pd.DataFrame)
        self.assertListEqual(df_res["smiles"].tolist(), ["ACDEFGHIK_SMI_CHG7.0", None])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
