.. _chem:

pepkit.chem
===========

The ``pepkit.chem`` module provides utilities for working with peptide and protein sequences, SMILES, standardization, and feature extraction.

Key Features
------------

- **Sequence/SMILES conversion:**  
  Convert between FASTA/sequence and canonical SMILES.
- **Property calculation:**  
  Compute net charge, molecular weight, and isoelectric point (pI) for peptide input.
- **Standardization:**  
  Filter/clean sequence data, optionally enforce canonical residues or pH charge state, with robust DataFrame and batch support.
- **Descriptor calculation:**  
  Generate sequence or molecule descriptors for ML applications with peptide or RDKit engines.

Sequence and SMILES Conversion
------------------------------

Convert a peptide sequence to canonical SMILES:

.. code-block:: python

   from pepkit.chem import fasta_to_smiles

   fasta = "ACDE"
   smiles = fasta_to_smiles(fasta)
   print(smiles)
   # Output: 'C[C@H](N)C(=O)N[C@@H](CS)C(=O)N[C@@H](CC(=O)O)C(=O)N[C@@H](CCC(=O)O)C(=O)O'

Convert back from SMILES to sequence (with optional FASTA header):

.. code-block:: python

   from pepkit.chem import smiles_to_fasta

   seq = smiles_to_fasta(smiles, header="peptide1")
   print(seq)
   # Output:
   # >peptide1
   # ACDE

Property Calculation
--------------------

Compute molecular properties from sequence, FASTA, or SMILES:

.. code-block:: python

   from pepkit.chem import compute_peptide_properties

   props = compute_peptide_properties("ACDE", pH=7.4)
   print(props)
   # Output: {'molecular_weight': 436.4430000000002, 'net_charge': -2, 'isoelectric_point': 3.8000000016763806}

Standardization and Filtering
-----------------------------

Standardize a list of peptide sequences (remove non-canonical, set charge by pH):

.. code-block:: python

   from pepkit.chem.standardize import Standardizer

   std = Standardizer(remove_non_canonical=True, charge_by_pH=True, pH=7.0)
   seqs = ["ACDEFGHIK", "XYZ"]
   standardized = std.process_list_fasta(seqs)
   print(standardized)
   # Output: ['CC[C@H](C)[C@H](NC(=O)[C@H](Cc1c[nH]cn1)NC(=O)CNC(=O)[C@H](Cc1ccccc1)NC(=O)[C@H](CCC(=O)[O-])NC(=O)[C@H](CC(=O)[O-])NC(=O)[C@H](CS)NC(=O)[C@H](C)[NH3+])C(=O)N[C@@H](CCCC[NH3+])C(=O)[O-]', None]

For pandas DataFrames:

.. code-block:: python

   import pandas as pd

   df = pd.DataFrame({'id': [1, 2], 'fasta': ["ACDEFGHIK", "XYZ"]})
   std = Standardizer(remove_non_canonical=True, charge_by_pH=True, pH=7.0)
   df_std = std.data_process(df, fasta_key='fasta')
   print(df_std)
   # Output: DataFrame with 'smiles' column standardized

Descriptor Calculation
----------------------

Calculate peptide or molecular descriptors:

.. code-block:: python

   from pepkit.chem.descriptor import Descriptor

   # Peptide descriptors
   data = [{"id": "pep1", "peptide_sequence": "ACDE"}]
   desc_pep = Descriptor(engine="peptides").calculate(data)
   print(desc_pep)

   # RDKit molecular descriptors
   data = [{"id": "mol1", "smiles": "CCO"}]
   desc_mol = Descriptor(engine="rdkit").calculate(data)
   print(desc_mol)

Testing and API Reference
-------------------------

See ``test/chem/`` for complete unittests and example-based validation.

Full function and class documentation: see `API Reference <https://Vivi-tran.github.io/PepKit/api.html>`_



