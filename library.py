import os
import pandas as pd
import logging
from datetime import datetime
from code.process_lib import process_csv, process_fasta 
from code.utils import filter

def setup_logger(log_file):
    """
    Set up the logger to write to both console and a log file.

    Args:
        log_file (str): Path to the log file.
    
    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger('CombineSequencesLogger')
    logger.setLevel(logging.DEBUG)  

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)  
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)  
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger

def combine_files(input_folder, combined_output_file, combined_log_file, filtered_output_file, filtered_log_file, logger):
    """
    Combine all CSV and FASTA files in the input folder into a single CSV file and filter sequences.

    Args:
        input_folder (str): Path to the input folder.
        combined_output_file (str): Path to the combined output CSV file.
        combined_log_file (str): Path to save the log file for the combined operation.
        filtered_output_file (str): Path to save the filtered (canonical) sequences CSV.
        filtered_log_file (str): Path to save the log file for non-canonical sequences.
        logger (logging.Logger): Logger for logging messages.
    """
    combined_df = pd.DataFrame(columns=['id', 'pep_seq'])
    logger.info(f"Starting to combine files from {input_folder}")

    # Combine CSV and FASTA files
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.join(root, file)
            filename, ext = os.path.splitext(file)
            prefix = filename  

            if ext.lower() == '.csv':
                logger.info(f"Processing CSV file: {file_path}")
                df = process_csv(file_path, prefix, logger)
                combined_df = pd.concat([combined_df, df], ignore_index=True)

            elif ext.lower() in ['.fasta', '.fa', '.fna', '.ffn', '.faa', '.frn']:
                logger.info(f"Processing FASTA file: {file_path}")
                df = process_fasta(file_path, prefix, logger)
                combined_df = pd.concat([combined_df, df], ignore_index=True)
            else:
                logger.warning(f"Unsupported file type {ext} for file {file_path}. Skipping.")

    # Identify and log duplicates based on 'id' column
    duplicate_mask = combined_df.duplicated(subset='id', keep='first')
    duplicates = combined_df[duplicate_mask]
    duplicate_ids = duplicates['id'].tolist()
    num_duplicates = len(duplicate_ids)

    if num_duplicates > 0:
        logger.info(f"Identified {num_duplicates} duplicate records")
        logger.debug("Duplicate IDs:")
        for dup_id in duplicate_ids:
            logger.debug(f"Duplicate ID removed: {dup_id}")
    else:
        logger.info("No duplicate records found")

    # Remove duplicates
    combined_df.drop_duplicates(subset='id', inplace=True)

    # Save the combined data to CSV
    try:
        combined_df.to_csv(combined_output_file, index=False)
        logger.info(f"Combined library saved to {combined_output_file}")
    except Exception as e:
        logger.error(f"Error writing to combined output file {combined_output_file}: {e}")

    # Filter canonical sequences and log non-canonical sequences
    filter(combined_output_file, filtered_output_file, filtered_log_file)
    logger.info(f"Filtered library saved to {filtered_output_file}")

def main():
    # Direct input and output file paths
    input_folder = "data/library/"  
    combined_output_file = "data/screen_in/library.csv"  
    filtered_output_file = "data/screen_in/library_filtered.csv"  
    combined_log_file = f"data/library/log_combined.txt"  
    filtered_log_file = f"data/screen_in/log_filtered.txt"  

    # Set up logger
    logger = setup_logger(combined_log_file)

    # Check if input folder exists
    if not os.path.isdir(input_folder):
        logger.error(f"The input folder {input_folder} does not exist or is not a directory.")
        return

    # Combine files and filter them
    combine_files(input_folder, combined_output_file, combined_log_file, filtered_output_file, filtered_log_file, logger)

if __name__ == "__main__":
    main()
