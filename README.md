# PepKit

**Toolkit for Peptide Modeling and Analysis**

![PepKit Logo](https://raw.githubusercontent.com/Vivi-tran/PepKit/main/Data/Figure/pepkit.png)

PepKit is a comprehensive Python package for peptide-centric workflows, including sequence parsing, format conversion, descriptor calculation, clustering, structural modeling, and docking protocols.

## Features

1. **Sequence I/O and Standardization**
   - Convert between FASTA and SMILES formats (`fasta_to_smiles`, `smiles_to_fasta`).
   - Standardize peptide sequences for downstream analysis.
2. **Descriptors and Clustering**
   - Compute physicochemical descriptors (e.g., molecular weight, hydrophobicity).
   - Cluster peptide libraries based on chemical similarity.
3. **Binding Affinity Metrics**
   - Calculate common metrics for peptide–target binding prediction.
   - Integrate with machine learning pipelines for affinity modeling.
4. **Structural Modeling**
   - Automated protocols for building peptide structures using AlphaFold and Rosetta.
   - Support for preparing input files and post-processing outputs.
5. **Docking Workflows**
   - High-throughput docking setup and analysis.
   - AlphaFold (AF) integration (under development) and Rosetta docking protocols.

## Installation

Install via pip:

```bash
pip install pepkit
```

Or clone the repository

```bash
git clone https://github.com/Vivi-tran/PepKit.git
cd PepKit
pip install -e .
```

## Quickstart
```python
from pepkit import fasta_to_smiles, smiles_to_fasta

# FASTA to SMILES
seq = "ACDEFGHIK"
smiles = fasta_to_smiles(seq)
print(f"SMILES: {smiles}")

```

## License

This project is licensed under MIT License - see the [License](LICENSE) file for details.