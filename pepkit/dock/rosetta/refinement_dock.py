from .prepack import prepack
from .refinement import rosetta_refinement
from .score import read_and_convert, get_optimal_clx
import logging
import os
from pepkit.io import setup_logging


def refinement_dock(
    path_to_main,
    path_to_db,
    input_pdb,
    prepack_out,
    refinement_out,
    nstruct=5,
):
    """
    Run the two-step Rosetta docking pipeline: prepack (global) + refinement (local).

    This function performs global docking (prepack) for a given input structure,
    identifies the lowest-scoring output, and then runs local refinement starting
    from the best global result.

    :param path_to_main: Path to the main RosettaScripts executable or protocol folder.
    :type path_to_main: str
    :param path_to_db: Path to the Rosetta database directory.
    :type path_to_db: str
    :param input_pdb: Path to the input PDB file to be docked.
    :type input_pdb: str
    :param prepack_out: Output directory for prepack (global docking) results.
    :type prepack_out: str
    :param refinement_out: Output directory for local refinement results.
    :type refinement_out: str
    :param nstruct: Number of refinement structures to generate (default: 5).
    :type nstruct: int
    :return: None

    Workflow
    --------
    1. Runs `prepack` on the input PDB.
    2. Parses prepack score file to find the optimal structure.
    3. Runs `rosetta_refinement` on the optimal structure from prepack.
    4. Logs progress and errors.
    :raises Exception: If any error occurs in docking or refinement.
    """
    setup_logging()

    try:
        # Perform global docking
        logging.info("Starting prepack...")
        prepack(
            path_to_main=path_to_main,
            input_pdb=input_pdb,
            path_to_db=path_to_db,
            output_dir=prepack_out,
        )

        df = read_and_convert(f"{prepack_out}/prepack.sc")
        prepack_optimal = get_optimal_clx(df)

        # Perform local docking using the optimal result from global docking
        logging.info("Starting refinement protocol...")

        rosetta_refinement(
            path_to_main=path_to_main,
            input_pdb=f"{prepack_out}/{prepack_optimal}.pdb",
            path_to_db=path_to_db,
            output_dir=refinement_out,
            nstruct=nstruct,
        )
        logging.info("Refinement docking completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the docking process: {e}")
        raise


def refinement_multiple_dock(
    path_to_main,
    path_to_db,
    pdb_dir,
    prepack_out,
    refinement_out,
    nstruct=5,
):
    """
    Batch run the two-step docking workflow for all PDB files in a directory.

    For each PDB file in `pdb_dir`, runs `refinement_dock` using distinct
    subfolders in the output directories. Progress and errors are logged.

    :param path_to_main: Path to the main RosettaScripts executable or protocol folder.
    :type path_to_main: str
    :param path_to_db: Path to the Rosetta database directory.
    :type path_to_db: str
    :param pdb_dir: Directory containing input PDB files to dock.
    :type pdb_dir: str
    :param prepack_out: Root directory for all prepack outputs.
    :type prepack_out: str
    :param refinement_out: Root directory for all refinement outputs.
    :type refinement_out: str
    :param nstruct: Number of refinement structures to generate for each input
    (default: 5).
    :type nstruct: int
    :return: None

    Workflow
    --------
    For each `.pdb` file in `pdb_dir`:
      1. Creates dedicated subdirectories for prepack and refinement.
      2. Runs `refinement_dock` for the input file.
      3. Logs errors and status for each file.
    :raises Exception: Any error during processing of a particular PDB will be logged
    but will not stop the batch.
    """
    setup_logging()
    # Ensure the input PDB directory exists
    if not os.path.exists(pdb_dir):
        logging.error(f"Input PDB directory does not exist: {pdb_dir}")
        return

    # Loop through all PDB files in the directory
    for pdb_file in os.listdir(pdb_dir):
        if pdb_file.endswith(".pdb"):
            pdb_id = os.path.splitext(pdb_file)[
                0
            ]  # Extract the file name without extension
            input_pdb_path = os.path.join(pdb_dir, pdb_file)
            prepack_out_path = os.path.join(prepack_out, pdb_id)
            refinement_out_path = os.path.join(refinement_out, pdb_id)

            try:
                logging.info(f"Starting docking for PDB ID: {pdb_id}")
                refinement_dock(
                    path_to_main=path_to_main,
                    path_to_db=path_to_db,
                    input_pdb=input_pdb_path,
                    prepack_out=prepack_out_path,
                    refinement_out=refinement_out_path,
                    nstruct=nstruct,
                )
            except Exception as e:
                logging.error(f"An error occurred while docking PDB ID {pdb_id}: {e}")
            else:
                logging.info(f"Successfully completed docking for PDB ID: {pdb_id}")
