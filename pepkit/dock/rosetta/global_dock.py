import os
import sys
import logging
import subprocess
from pepkit.io import setup_logging, validate_path


def rosetta_global_dock(
    path_to_main,
    input_pdb,
    output_dir=".",
    nstruct=10,
    pep_seq_id="A",
    pro_seq_id="B",
    extra_options=None,
    log_level=logging.INFO,
):
    setup_logging(level=log_level)
    validate_path(path_to_main)
    validate_path(input_pdb)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Output directory {output_dir} created.")

    platform = sys.platform
    if platform.startswith("darwin"):
        binary_suffix = "macosclangrelease"
    elif platform.startswith("linux"):
        binary_suffix = "linuxgccrelease"
    elif platform.startswith("win"):
        binary_suffix = "windowsrelease"
    else:
        logging.error(f"Unsupported platform: {platform}")
        raise ValueError(f"Unsupported platform: {platform}")

    executable = f"{path_to_main}/source/bin/docking_protocol.{binary_suffix}"
    partners = f"{pep_seq_id}_{pro_seq_id}"
    basic_cmd = [
        executable,
        "-s",
        input_pdb,
        "-partners",
        partners,
        "-docking:randomize1",
        "-docking:randomize2",
        "-ex1",
        "-ex2",
        "-use_input_sc",
        "-nstruct",
        str(nstruct),
        "-out:path:pdb",
        output_dir,
        "-out:file:scorefile",
        f"{output_dir}/docking_scores.fasc",
    ]

    if extra_options:
        basic_cmd.extend(extra_options)

    logging.info(f"Executing command: {' '.join(basic_cmd)}")

    try:
        result = subprocess.run(
            basic_cmd,
            text=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logging.info("Rosetta execution successful")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"An error occurred: {e.stderr}")
        return None


# if __name__ == "__main__":
#     rosetta_global_dock(
#         path_to_main="/Users/tieulongphan/Downloads/rosetta.binary.m1.release-371/main",
#         # platform="macos",
#         input_pdb="pepdock/1du3_pep_min.pdb",
#         output_dir="./pdb",
#         pep_seq_id="A",
#         pro_seq_id="B",
#     )
