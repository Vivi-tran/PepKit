from rdkit import Chem
from rdkit.Chem import Descriptors
from pepkit.chem._parser import fasta_to_smiles
from pepkit.chem.standardize import Standardizer


def _to_smiles(input_str: str) -> str:
    """
    Convert a FASTA, peptide sequence, or SMILES string to a canonical SMILES.

    Attempts to detect the type of input:
    - If FASTA format (starts with '>'), parses as FASTA using `fasta_to_smiles`.
    - If a valid peptide sequence, converts using RDKit's `Chem.MolFromSequence`.
    - Otherwise, returns the input unchanged, assuming it is a SMILES string.

    :param input_str: Input string (FASTA record, sequence, or SMILES).
    :type input_str: str
    :raises ValueError: If FASTA or sequence cannot be parsed.
    :return: Canonical SMILES string.
    :rtype: str
    """

    s = input_str.strip()
    if s.startswith(">"):
        # FASTA record
        return fasta_to_smiles(s)
    # try as sequence
    mol_seq = Chem.MolFromSequence(s)
    if mol_seq:
        return Chem.MolToSmiles(mol_seq, canonical=True, isomericSmiles=True)
    # assume SMILES
    return s


def compute_net_charge(input_str: str, pH: float = 7.4) -> float:
    """
    Estimate the net formal charge of a peptide at a given pH.

    Converts the input to SMILES, re-protonates using the specified pH,
    and sums the formal atomic charges in the resulting molecule.

    :param input_str: Input as FASTA, sequence, or SMILES.
    :type input_str: str
    :param pH: pH value for charge calculation.
    :type pH: float
    :raises ValueError: If charged SMILES cannot be parsed.
    :return: Net formal charge (sum of atomic charges).
    :rtype: float
    """

    smi = _to_smiles(input_str)
    charged_smi = Standardizer(charge_by_pH=True).add_charge_by_pH(smi, pH)
    mol = Chem.MolFromSmiles(charged_smi)
    if mol is None:
        raise ValueError(f"Could not parse charged SMILES: {charged_smi!r}")
    return sum(atom.GetFormalCharge() for atom in mol.GetAtoms())


def compute_molecular_weight(input_str: str) -> float:
    """
    Calculate the average molecular weight of a peptide.

    Converts the input (FASTA, sequence, or SMILES) to a molecule,
    then calculates its molecular weight using RDKit.

    :param input_str: FASTA record, peptide sequence, or SMILES string.
    :type input_str: str
    :raises ValueError: If input cannot be parsed to a molecule.
    :return: Molecular weight in Daltons.
    :rtype: float
    """

    smi = _to_smiles(input_str)
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        raise ValueError(f"Could not parse input for molecular weight: {input_str!r}")
    return Descriptors.MolWt(mol)


def compute_peptide_properties(input_str: str, pH: float = 7.4) -> dict:
    """
    Compute basic properties of a peptide: molecular weight, net charge,
    and isoelectric point (pI).

    - Molecular weight is computed via RDKit's Descriptors.MolWt.
    - Net charge is estimated at the specified pH.
    - Isoelectric point (pI) is approximated by numerically finding
    the pH at which the net charge is zero.

    :param input_str: Peptide input (FASTA, sequence, or SMILES).
    :type input_str: str
    :param pH: pH value for net charge calculation and initial guess for pI.
    :type pH: float
    :return: Dictionary with 'molecular_weight', 'net_charge', and 'isoelectric_point'.
    :rtype: dict
    """

    mw = compute_molecular_weight(input_str)
    charge = compute_net_charge(input_str, pH)

    # Approximate pI via bisection
    def net_at(ph):
        return compute_net_charge(input_str, ph)

    lo, hi = 0.0, 14.0
    for _ in range(30):
        mid = (lo + hi) / 2
        if net_at(mid) > 0:
            lo = mid
        else:
            hi = mid
    pI = (lo + hi) / 2
    return {
        "molecular_weight": mw,
        "net_charge": charge,
        "isoelectric_point": pI,
    }
