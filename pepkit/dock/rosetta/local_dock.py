import os
import sys
import logging
import subprocess
from pepkit.io import setup_logging, validate_path


def rosetta_local_dock(
    path_to_main,
    input_pdb,
    xml_protocol,
    output_dir="./pdb",
    nstruct=10,
    extra_options=None,
    log_level=logging.INFO,
):
    setup_logging(level=log_level)
    validate_path(path_to_main)
    validate_path(input_pdb)
    validate_path(xml_protocol)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Output directory {output_dir} created.")

    platform = sys.platform
    binary_suffix = ""
    if platform.startswith("darwin"):
        binary_suffix = "macosclangrelease"
    elif platform.startswith("linux"):
        binary_suffix = "linuxgccrelease"
    elif platform.startswith("win"):
        binary_suffix = "windowsrelease"
    else:
        logging.error(f"Unsupported platform: {platform}")
        raise ValueError(f"Unsupported platform: {platform}")

    executable = f"{path_to_main}/source/bin/rosetta_scripts.{binary_suffix}"
    basic_cmd = [
        executable,
        "-s",
        input_pdb,
        "-parser:protocol",
        xml_protocol,
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
