import logging
from typing import Set, Optional, Dict, Any, List, Union
from openbabel import pybel
from openbabel import openbabel as ob
from joblib import Parallel, delayed
import pandas as pd
from pepkit.chem import fasta_to_smiles

# Set of 20 canonical amino acid one-letter codes
_CANONICAL_AA: Set[str] = set("ACDEFGHIKLMNPQRSTVWY")


class Standardizer:
    """
    Utility for processing peptide/protein sequences:
    - Validate canonical sequences
    - Convert FASTA to SMILES
    - Add pH-dependent charges
    - Batch and dict/DataFrame-based processing

    :param remove_non_canonical: If True, filter out non-canonical sequences
    :type remove_non_canonical: bool
    :param charge_by_pH: If True, adjust SMILES charges at given pH
    :type charge_by_pH: bool
    :param pH: pH value for charge adjustment
    :type pH: float
    :param logger: Logger instance for status messages
    :type logger: logging.Logger
    """

    def __init__(
        self,
        remove_non_canonical: bool = False,
        charge_by_pH: bool = False,
        pH: float = 7.4,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Initialize the Standardizer.

        :param remove_non_canonical: Exclude sequences with non-canonical residues
        :param charge_by_pH: Enable pH-based charge adjustment of SMILES
        :param pH: pH at which to perform charge adjustment
        :param logger: Optional logger for informative output
        """
        self.remove_non_canonical = remove_non_canonical
        self.charge_by_pH = charge_by_pH
        self.pH = pH
        self.logger = logger or logging.getLogger(__name__)

    @staticmethod
    def is_canonical_sequence(sequence: str) -> bool:
        """
        Check if a sequence contains only canonical amino acids.

        :param sequence: FASTA-style one-letter amino acid sequence
        :type sequence: str
        :return: True if all residues are canonical
        :rtype: bool
        :raises TypeError: If sequence is not a string
        """
        if not isinstance(sequence, str):
            raise TypeError(
                f"Expected a string sequence, got {type(sequence).__name__}"
            )
        return all(residue in _CANONICAL_AA for residue in sequence.upper())

    @staticmethod
    def add_charge_by_pH(smi: str, pH: float = 7.4) -> str:
        """
        Adjust the protonation state of a SMILES string for a given pH.

        :param smi: Input SMILES string
        :type smi: str
        :param pH: Target pH for protonation correction
        :type pH: float
        :return: pH-corrected SMILES string
        :rtype: str
        """
        mol = pybel.readstring("smi", smi)
        obmol = mol.OBMol

        phmodel = ob.OBPhModel()
        phmodel.Init()
        phmodel.CorrectForPH(obmol, pH)

        # Refresh explicit hydrogens
        obmol.DeleteHydrogens()
        obmol.AddHydrogens(False, True, pH)

        return pybel.Molecule(obmol).write("smi").strip()

    @staticmethod
    def process_fasta(
        fasta: str,
        remove_non_canonical: bool = False,
        charge_by_pH: bool = False,
        pH: float = 7.4,
    ) -> Optional[str]:
        """
        Convert a FASTA sequence to a SMILES string, with optional filtering and charging.

        :param fasta: FASTA-style amino acid sequence
        :type fasta: str
        :param remove_non_canonical: If True, skip sequences containing
        non-canonical residues
        :type remove_non_canonical: bool
        :param charge_by_pH: If True, adjust SMILES at specified pH
        :type charge_by_pH: bool
        :param pH: pH for protonation adjustment
        :type pH: float
        :return: Generated SMILES or None if filtered out
        :rtype: Optional[str]
        """
        if remove_non_canonical and not Standardizer.is_canonical_sequence(fasta):
            return None

        smiles = fasta_to_smiles(fasta)
        if charge_by_pH:
            smiles = Standardizer.add_charge_by_pH(smiles, pH)
        return smiles

    @staticmethod
    def dict_process(
        data: List[Dict[str, Any]],
        fasta_key: str,
        remove_non_canonical: bool = False,
        charge_by_pH: bool = False,
        pH: float = 7.4,
    ) -> List[Dict[str, Any]]:
        """
        Process a list of dictionaries, converting FASTA sequences to SMILES.

        :param data: List of records (dicts) containing FASTA sequences
        :type data: List[Dict[str, Any]]
        :param fasta_key: Key in each dict for the FASTA sequence
        :type fasta_key: str
        :param remove_non_canonical: Remove non-canonical sequences if True
        :type remove_non_canonical: bool
        :param charge_by_pH: Adjust SMILES at specified pH if True
        :type charge_by_pH: bool
        :param pH: pH value for charge adjustment
        :type pH: float
        :return: New list of dicts with 'smiles' field added
        :rtype: List[Dict[str, Any]]
        :raises KeyError: If fasta_key is missing in any record
        """
        processed = []
        for record in data:
            if fasta_key not in record:
                raise KeyError(f"Record missing key {fasta_key!r}")
            fasta_seq = record[fasta_key]
            smiles = Standardizer.process_fasta(
                fasta_seq,
                remove_non_canonical,
                charge_by_pH,
                pH,
            )
            new_rec = dict(record)
            new_rec["smiles"] = smiles
            processed.append(new_rec)
        return processed

    def process_list_fasta(
        self,
        sequences: List[str],
        n_jobs: int = -1,
    ) -> List[Optional[str]]:
        """
        Process a list of FASTA sequences in parallel.

        :param sequences: List of FASTA sequences
        :type sequences: List[str]
        :param n_jobs: Number of parallel jobs for processing
        :type n_jobs: int
        :return: List of resulting SMILES or None values
        :rtype: List[Optional[str]]
        """
        results = Parallel(n_jobs=n_jobs)(
            delayed(Standardizer.process_fasta)(
                seq, self.remove_non_canonical, self.charge_by_pH, self.pH
            )
            for seq in sequences
        )
        return results

    def data_process(
        self,
        data: Union[pd.DataFrame, List[Dict[str, Any]]],
        fasta_key: str = "fasta",
        n_jobs: int = -1,
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Process FASTA data in a DataFrame or list of dicts, adding SMILES output.

        :param data: Input pandas DataFrame or list of dicts with FASTA sequences
        :type data: Union[pd.DataFrame, List[Dict[str, Any]]]
        :param fasta_key: Column/key for FASTA sequences in the data
        :type fasta_key: str
        :param n_jobs: Number of parallel jobs for charge adjustment
        :type n_jobs: int
        :return: DataFrame or list of dicts with 'smiles' column/field
        :rtype: Union[pd.DataFrame, List[Dict[str, Any]]]
        """
        is_dataframe = isinstance(data, pd.DataFrame)
        if is_dataframe:
            records = data.to_dict(orient="records")
        else:
            records = data

        # Only process/charge in process_fasta, not again!
        processed = self.dict_process(
            records,
            fasta_key,
            self.remove_non_canonical,
            self.charge_by_pH,
            self.pH,
        )

        if is_dataframe:
            return pd.DataFrame(processed)
        return processed
