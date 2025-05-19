Dock
====

PepKit provides wrappers and utilities for running peptide docking and refinement using Rosetta, as well as tools to extract and analyze docking scores.

Rosetta Refinement
-------------------

Use `refinement_multiple_dock` to launch Rosetta's refinement docking protocol on multiple PDB files in batch mode.

**Function signature**::

    refinement_multiple_dock(
        path_to_main,
        path_to_db,
        pdb_dir,
        prepack_out,
        refinement_out,
        nstruct=1,
    )

**Parameters:**

  - `path_to_main`: Path to the main Rosetta executable directory.
  - `path_to_db`: Path to the Rosetta database directory.
  - `pdb_dir`: Directory containing input PDB files.
  - `prepack_out`: Output directory for prepacked structures.
  - `refinement_out`: Output directory for refined complexes.
  - `nstruct`: Number of output structures per input (default: 1).


**Example:**

.. code-block:: python

    from pepkit.dock.rosetta.refinement_dock import refinement_multiple_dock
    from pepkit.examples import rosetta_data

    # Example: get test PDB directory and run docking
    pdb_path = rosetta_data.get_rosetta_ex_path()
    refinement_multiple_dock(
        path_to_main="/path/to/rosetta/main",
        path_to_db="/path/to/rosetta/main/database",
        pdb_dir=pdb_path,
        prepack_out="data/rosetta_test/prepack",
        refinement_out="data/rosetta_test/refinement",
        nstruct=1,
    )

Score Extraction Utilities
--------------------------

Utilities for reading, converting, and analyzing Rosetta docking scorefiles.

- `read_and_convert(scorefile)`: Reads a single Rosetta scorefile and returns a DataFrame.
- `extract_score(score_dir)`: Aggregates all scorefiles in a directory into a single DataFrame.
- `get_optimal_clx(df)`: Retrieves the optimal complex (e.g., by lowest energy score) from a score DataFrame.

**Example:**

.. code-block:: python

    import os
    from pepkit.dock.rosetta.score import read_and_convert, extract_score, get_optimal_clx
    from pepkit.examples import rosetta_data

    TEST_DIR = rosetta_data.get_refinement_path()   # Gets the example refinement directory
    TEST_SCORE = os.path.join(TEST_DIR, "complex_1", "docking_scores.sc")

    # Read and convert a single scorefile
    df = read_and_convert(TEST_SCORE)
    print(df.head())

    # Aggregate all scores in a directory
    df_all = extract_score(TEST_DIR)
    print(df_all.head())

    # Get the optimal complex (best score)
    opt = get_optimal_clx(df)
    print("Optimal structure:", opt)

**Typical usage pattern:**

1. Run Rosetta docking using `refinement_multiple_dock`.
2. Extract and analyze scores using `read_and_convert`, `extract_score`, and `get_optimal_clx`.

Testing and API Reference
-------------------------

- See ``test/metrics/`` for complete unittests and example-based validation.
- Full function and class documentation: see `API Reference <https://Vivi-tran.github.io/PepKit/api.html>`_
