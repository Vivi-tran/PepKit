import unittest
from rdkit import Chem
from pepkit.chem._property import (
    _to_smiles,
    compute_net_charge,
    compute_molecular_weight,
    compute_peptide_properties,
)


class TestPeptideProperty(unittest.TestCase):
    def setUp(self):
        # Example peptide: Alanine-Cysteine-Aspartic acid
        self.sequence = "ACD"
        self.fasta = ">pep1\nACD\n"
        # SMILES for ACD from RDKit
        mol = Chem.MolFromSequence(self.sequence)
        self.smiles = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)

    def test_to_smiles_sequence(self):
        smi = _to_smiles(self.sequence)
        self.assertIsInstance(smi, str)
        self.assertEqual(smi, self.smiles)

    def test_to_smiles_fasta(self):
        smi = _to_smiles(self.fasta)
        self.assertIsInstance(smi, str)
        self.assertEqual(smi, self.smiles)

    def test_to_smiles_smiles(self):
        smi = _to_smiles(self.smiles)
        self.assertEqual(smi, self.smiles)

    def test_compute_molecular_weight_sequence_vs_fasta(self):
        mw_seq = compute_molecular_weight(self.sequence)
        mw_fasta = compute_molecular_weight(self.fasta)
        # Values should match
        self.assertAlmostEqual(mw_seq, mw_fasta, places=5)
        # Known approximate weight > 0
        self.assertGreater(mw_seq, 0)

    def test_compute_net_charge(self):
        charge_seq = compute_net_charge(self.sequence, pH=7.4)
        charge_fasta = compute_net_charge(self.fasta, pH=7.4)
        self.assertEqual(charge_seq, -1)
        self.assertEqual(charge_fasta, -1)

    def test_compute_peptide_properties_keys_and_types(self):
        props = compute_peptide_properties(self.sequence, pH=7.4)
        # Check keys
        self.assertIn("molecular_weight", props)
        self.assertIn("net_charge", props)
        self.assertIn("isoelectric_point", props)
        # Check types
        self.assertIsInstance(props["molecular_weight"], float)
        self.assertIsInstance(props["net_charge"], (int, float))
        self.assertIsInstance(props["isoelectric_point"], float)

    def test_compute_peptide_properties_consistency(self):
        props_seq = compute_peptide_properties(self.sequence, pH=7.4)
        props_fasta = compute_peptide_properties(self.fasta, pH=7.4)
        # MW and charge should match
        self.assertAlmostEqual(
            props_seq["molecular_weight"], props_fasta["molecular_weight"], places=5
        )
        self.assertEqual(props_seq["net_charge"], props_fasta["net_charge"])


if __name__ == "__main__":
    unittest.main()
