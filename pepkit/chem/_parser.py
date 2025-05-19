import numpy as np
from rdkit import Chem


def fasta_to_smiles(fasta: str) -> str:
    """
    Convert a peptide/protein FASTA sequence into a canonical SMILES string using RDKit.

    This function uses RDKit's `Chem.MolFromFASTA` to parse the FASTA string
    into a molecule object, then returns its canonical SMILES representation
    using `Chem.MolToSmiles`.

    :param fasta: FASTA-format amino acid sequence (1-letter codes, no header required).
    :type fasta: str
    :raises ValueError: If the sequence cannot be parsed as a peptide/protein.
    :return: Canonical SMILES string corresponding to the input peptide.
    :rtype: str
    """
    mol = Chem.MolFromFASTA(fasta)
    if mol is None:
        raise ValueError(f"Could not parse FASTA:\n{fasta!r}")
    return Chem.MolToSmiles(mol, canonical=True)


def smiles_to_fasta(smiles: str, header: str = None) -> str:
    """
    Convert a SMILES string for a peptide to a FASTA record using RDKit.

    This function converts the given SMILES to an RDKit molecule,
    retrieves the amino acid sequence with `MolToSequence`, and
    emits a FASTA-formatted string. An optional header line (e.g. '>peptide1')
    can be included.

    :param smiles: Canonical SMILES string for a peptide or protein.
    :type smiles: str
    :param header: Optional header for the FASTA record (without '>').
    :type header: str, optional
    :raises ValueError: If SMILES cannot be parsed or not a peptide.
    :return: FASTA record string (with optional header).
    :rtype: str
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Could not parse SMILES: {smiles!r}")
    seq = Chem.MolToSequence(mol)
    if not seq:
        raise ValueError(
            "RDKit MolToSequence returned no sequence; is this really a peptide?"
        )
    header_str = f">{header}\n" if header is not None else ""
    return f"{header_str}{seq}\n"


def kd_to_pkd(kd):
    r"""
    Convert a dissociation constant (K\ :sub:`d`\ ) in molar units to pK\ :sub:`d`\.

    The conversion is performed as: pK\ :sub:`d`\ = -log10(K\ :sub:`d`\ [M] / 1e-9)
    (i.e., convert K\ :sub:`d`\ from M to nM before taking log).

    :param kd: Dissociation constant (K_d) in molar units (M).
    :type kd: float or array-like
    :return: The corresponding pK_d value(s).
    :rtype: float or numpy.ndarray

    Example
    -------
    >>> kd_to_pkd(1e-9)
    9.0
    >>> kd_to_pkd(50e-9)
    7.30103...
    """
    return -np.log10(kd * 1e9)
