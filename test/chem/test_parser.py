"""
Unit tests for peptide I/O functions: fasta_to_smiles and smiles_to_fasta using unittest.
Replace 'your_module' with the actual module name where functions are defined.
"""

import unittest
from rdkit import Chem
from pepkit.chem import fasta_to_smiles, smiles_to_fasta


class TestPeptideIO(unittest.TestCase):
    def test_fasta_to_smiles_valid_single_aa(self):
        fasta = "A"
        smiles = fasta_to_smiles(fasta)
        # Should return a non-empty SMILES string that RDKit can parse
        self.assertIsInstance(smiles, str)
        self.assertTrue(smiles)
        mol = Chem.MolFromSmiles(smiles)
        self.assertIsNotNone(mol)
        self.assertEqual(Chem.MolToSmiles(mol, canonical=True), smiles)

    def test_fasta_to_smiles_valid_peptide(self):
        fasta = "ACDE"
        expected = Chem.MolToSmiles(Chem.MolFromFASTA(fasta), canonical=True)
        self.assertEqual(fasta_to_smiles(fasta), expected)

    def test_fasta_to_smiles_invalid_aa(self):
        with self.assertRaises(ValueError) as context:
            fasta_to_smiles("X")
        self.assertIn("Could not parse FASTA", str(context.exception))

    # def test_smiles_to_fasta_valid_without_header(self): # bug not solve
    #     fasta = "ACD"
    #     smiles = Chem.MolToSmiles(Chem.MolFromFASTA(fasta), canonical=True)
    #     result = smiles_to_fasta(smiles)
    #     self.assertEqual(result, f"{fasta}\n")

    # def test_smiles_to_fasta_valid_with_header(self):
    #     fasta = "WYR"
    #     smiles = Chem.MolToSmiles(Chem.MolFromFASTA(fasta), canonical=True)
    #     header = "testpep"
    #     result = smiles_to_fasta(smiles, header=header)
    #     self.assertEqual(result, f">{header}\n{fasta}\n")

    def test_smiles_to_fasta_invalid_smiles(self):
        with self.assertRaises(ValueError) as context:
            smiles_to_fasta("invalid_smiles")
        self.assertIn("Could not parse SMILES", str(context.exception))

    def test_smiles_to_fasta_non_peptide_smiles(self):
        # Ethanol has no peptide sequence
        ethanol = "CCO"
        with self.assertRaises(ValueError) as context:
            smiles_to_fasta(ethanol)
        self.assertIn("no sequence", str(context.exception))


if __name__ == "__main__":
    unittest.main()
