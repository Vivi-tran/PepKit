import pandas as pd
import logging

def filter(input_file, canonical_output, log_file):
    """
    Preprocesses a combined CSV file to filter sequences with non-canonical amino acids and invalid lengths.

    Args:
        input_file (str): Path to the input combined CSV file.
        canonical_output (str): Path to save the canonical sequences CSV.
        log_file (str): Path to save the log file for non-canonical sequences.
    """
    # Define the set of canonical amino acids
    canonical_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")

    # Initialize logging
    logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(message)s')
    
    # Read input CSV file
    df = pd.read_csv(input_file)
    logging.info(f"Loaded {len(df)} records from input file.")

    non_canonical_log = []
    canonical_rows = []

    # Process each sequence in the dataframe
    for index, row in df.iterrows():
        pep_seq = row['pep_seq']
        
        # Check if the sequence contains non-canonical amino acids or is of invalid length
        if any(aa not in canonical_amino_acids for aa in pep_seq) or len(pep_seq) < 2 or len(pep_seq) > 30:
            non_canonical_log.append(f"{row['id']}: {pep_seq}")
            logging.debug(f"Non-canonical sequence: {row['id']} ({pep_seq})")
        else:
            canonical_rows.append(row)

    # Save canonical sequences to a new CSV file
    canonical_df = pd.DataFrame(canonical_rows)
    canonical_df.to_csv(canonical_output, index=False)
    logging.info(f"Canonical sequences saved to '{canonical_output}' with {len(canonical_rows)} entries.")

    # Write non-canonical sequences to the log file
    with open(log_file, 'w') as log:
        log.write('\n'.join(non_canonical_log))
    logging.info(f"Non-canonical sequences logged in '{log_file}' with {len(non_canonical_log)} entries.")