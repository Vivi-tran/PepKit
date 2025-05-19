from .global_dock import rosetta_global_dock
from .local_dock import rosetta_local_dock
from .score import read_and_convert, get_optimal_clx
import logging
import os
from pepkit.io import setup_logging


def rosetta_peptide_dock(
    path_to_main,
    input_pdb,
    global_out,
    pep_seq_id,
    pro_seq_id,
    xml_protocol,
    local_out,
    nstruct=10,
):
    setup_logging()

    try:
        # Perform global docking
        logging.info("Starting global docking...")
        rosetta_global_dock(
            path_to_main=path_to_main,
            input_pdb=input_pdb,
            output_dir=global_out,
            pep_seq_id=pep_seq_id,
            pro_seq_id=pro_seq_id,
            nstruct=nstruct,
        )

        # Read and analyze the global docking results
        logging.info("Reading and converting global docking scores...")
        df = read_and_convert(f"{global_out}/docking_scores.fasc")
        optimal_global = get_optimal_clx(df)
        logging.info(f"Optimal complex from global docking: {optimal_global}")

        # Perform local docking using the optimal result from global docking
        logging.info("Starting local docking...")
        rosetta_local_dock(
            path_to_main=path_to_main,
            input_pdb=f"{global_out}/{optimal_global}.pdb",
            xml_protocol=xml_protocol,
            output_dir=local_out,
            nstruct=nstruct,
        )
        logging.info("Local docking completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the docking process: {e}")
        raise


def rosetta_multiple_dock(
    path_to_main,
    pdb_dir,
    global_out,
    pep_seq_id,
    pro_seq_id,
    xml_protocol,
    local_out,
    nstruct=10,
):
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
            global_out_path = os.path.join(global_out, pdb_id)
            local_out_path = os.path.join(local_out, pdb_id)

            try:
                logging.info(f"Starting docking for PDB ID: {pdb_id}")
                rosetta_peptide_dock(
                    path_to_main=path_to_main,
                    input_pdb=input_pdb_path,
                    global_out=global_out_path,
                    pep_seq_id=pep_seq_id,
                    pro_seq_id=pro_seq_id,
                    xml_protocol=xml_protocol,
                    local_out=local_out_path,
                    nstruct=nstruct,
                )
            except Exception as e:
                logging.error(f"An error occurred while docking PDB ID {pdb_id}: {e}")
            else:
                logging.info(f"Successfully completed docking for PDB ID: {pdb_id}")
