import pandas as pd
from peptides import Peptide
from rdkit import Chem
from rdkit.Chem import Descriptors
from joblib import Parallel, delayed
from typing import List, Dict, Union, Any


class Descriptor:
    """
    Compute molecular or peptide descriptors for a collection of records.

    This class provides descriptor calculation for peptides or small molecules,
    supporting two engines:
      - 'peptides': Uses the `peptides` Python package for peptide descriptors.
      - 'rdkit': Uses RDKit for general molecular descriptors from SMILES.

    :param engine: Descriptor engine ('peptides' for peptide descriptors,
    'rdkit' for molecular descriptors).
    :type engine: str
    :param fasta_key: Key for the peptide sequence in input records or DataFrame.
    :type fasta_key: str
    :param id_key: Key for unique record identifiers in input.
    :type id_key: str
    :param smiles_key: Key for SMILES string in input records (used only by 'rdkit').
    :type smiles_key: str

    Example
    -------
    >>> descriptor = Descriptor(engine='peptides')
    >>> records = [{'id': 1, 'peptide_sequence': 'ACDE'}]
    >>> df_out = descriptor.calculate(records, n_jobs=2)
    >>> descriptor = Descriptor(engine='rdkit')
    >>> records = [{'id': 1, 'smiles': 'CC(=O)O'}]
    >>> df_out = descriptor.calculate(records, n_jobs=4)
    """

    SUPPORTED_ENGINES = {"peptides", "rdkit"}

    def __init__(
        self,
        engine: str = "peptides",
        fasta_key: str = "peptide_sequence",
        id_key: str = "id",
        smiles_key: str = "smiles",
    ) -> None:
        """
        Initialize the Descriptor calculator.

        :param engine: Descriptor engine to use ('peptides' or 'rdkit').
        :type engine: str
        :param fasta_key: Sequence key in each record (for both engines).
        :type fasta_key: str
        :param id_key: ID key in each record.
        :type id_key: str
        :param smiles_key: SMILES key in each record (used only by 'rdkit').
        :type smiles_key: str
        :raises ValueError: If unsupported engine is specified.
        """
        engine = engine.lower()
        if engine not in self.SUPPORTED_ENGINES:
            raise ValueError(
                f"Unsupported engine '{engine}'. Choose from {self.SUPPORTED_ENGINES}."
            )
        self.engine = engine
        self.fasta_key = fasta_key
        self.id_key = id_key
        self.smiles_key = smiles_key

    @staticmethod
    def _calc_peptide_record(
        record: Dict[str, Any], fasta_key: str, id_key: str
    ) -> Dict[str, Any]:
        """
        Compute peptide-specific descriptors using the `peptides` library.

        :param record: Input record with sequence and ID.
        :type record: dict
        :param fasta_key: Key for sequence in the record.
        :type fasta_key: str
        :param id_key: Key for record ID.
        :type id_key: str
        :raises KeyError: If required fields are missing.
        :return: Descriptor dictionary with sequence and ID fields.
        :rtype: dict

        Example
        -------
        >>> Descriptor._calc_peptide_record({'id': 1, 'peptide_sequence': 'ACD'},
        'peptide_sequence', 'id')
        {'id': 1, 'peptide_sequence': 'ACD', ...}
        """
        seq = record.get(fasta_key)
        pid = record.get(id_key)
        if seq is None:
            raise KeyError(
                f"Missing sequence under key '{fasta_key}' in record {record}"
            )
        if pid is None:
            raise KeyError(f"Missing ID under key '{id_key}' in record {record}")
        pep = Peptide(seq)
        desc = pep.descriptors()
        desc[id_key] = pid
        desc[fasta_key] = seq
        return desc

    @staticmethod
    def _calc_rdkit_record(
        record: Dict[str, Any], smiles_key: str, id_key: str
    ) -> Dict[str, Any]:
        """
        Compute RDKit descriptors for a single record.

        :param record: Input record with SMILES and ID.
        :type record: dict
        :param smiles_key: Key for SMILES string in the record.
        :type smiles_key: str
        :param id_key: Key for record ID.
        :type id_key: str
        :raises KeyError: If required fields are missing.
        :raises ValueError: If SMILES cannot be parsed.
        :return: Descriptor dictionary with SMILES and ID fields.
        :rtype: dict

        Example
        -------
        >>> Descriptor._calc_rdkit_record({'id': 1, 'smiles': 'CC(=O)O'}, 'smiles', 'id')
        {'id': 1, 'smiles': 'CC(=O)O', ...}
        """
        smi = record.get(smiles_key)
        pid = record.get(id_key)
        if smi is None:
            raise KeyError(
                f"Missing SMILES under key '{smiles_key}' in record {record}"
            )
        if pid is None:
            raise KeyError(f"Missing ID under key '{id_key}' in record {record}")
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            raise ValueError(f"Invalid SMILES string '{smi}' in record {record}")
        desc: Dict[str, Any] = {}
        for name, func in Descriptors._descList:
            try:
                desc[name] = func(mol)
            except Exception:
                desc[name] = None
        desc[id_key] = pid
        desc[smiles_key] = smi
        return desc

    def calculate(
        self,
        data: Union[pd.DataFrame, List[Dict[str, Any]]],
        n_jobs: int = 1,
        verbose: int = 0,
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Compute descriptors in parallel for all records in `data`.

        The output type matches the input type: if you provide a DataFrame,
        you get a DataFrame; if you provide a list of dicts, you get a list.

        :param data: Input data (pandas DataFrame or list of dicts), with fields
        for sequence/SMILES and ID.
        :type data: Union[pd.DataFrame, List[Dict[str, Any]]]
        :param n_jobs: Number of parallel jobs (joblib, -1 uses all available cores).
        :type n_jobs: int
        :param verbose: Verbosity for joblib parallel execution.
        :type verbose: int
        :raises TypeError: If input is not a DataFrame or list of dicts.
        :raises KeyError: If required keys are missing in input records.
        :raises ValueError: If SMILES cannot be parsed by RDKit.
        :return: Descriptor results, in the same format as the input.
        :rtype: Union[pd.DataFrame, List[Dict[str, Any]]]

        Example
        -------
        >>> descriptor = Descriptor(engine='peptides')
        >>> df = pd.DataFrame([{'id': 1, 'peptide_sequence': 'ACDE'}])
        >>> result = descriptor.calculate(df, n_jobs=1)
        """
        if isinstance(data, pd.DataFrame):
            records = data.to_dict(orient="records")
            as_dataframe = True
        elif isinstance(data, list):
            records = data
            as_dataframe = False
        else:
            raise TypeError("`data` must be a pandas.DataFrame or a list of dicts")

        def peptide_worker(rec):
            return Descriptor._calc_peptide_record(rec, self.fasta_key, self.id_key)

        def rdkit_worker(rec):
            return Descriptor._calc_rdkit_record(rec, self.smiles_key, self.id_key)

        if self.engine == "peptides":
            worker_func = peptide_worker
        else:
            worker_func = rdkit_worker

        results = Parallel(n_jobs=n_jobs, verbose=verbose)(
            delayed(worker_func)(rec) for rec in records
        )

        return pd.DataFrame(results) if as_dataframe else results
