import pandas as pd


def process_csv(file_path, prefix, logger):
    """
    Process a CSV file to extract 'id' and 'sequence' columns based on substring matching.
    Any column name containing 'id' or 'sequence' (case-insensitive) is considered.

    Args:
        file_path (str): Path to the CSV file.
        prefix (str): Prefix to add to each 'id'.
        logger (logging.Logger): Logger for logging messages.

    Returns:
        pd.DataFrame: DataFrame with 'id' and 'pep_seq' columns.
    """
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Successfully read CSV file: {file_path}")
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {e}")
        return pd.DataFrame(columns=["id", "pep_seq"])

    # Standardize column names to lower case for comparison
    lower_columns = [col.lower() for col in df.columns]

    # Initialize variables to store the actual column names
    id_col = None
    seq_col = None

    # Identify the 'id' column: first column containing 'id' in its name
    for original_col, lower_col in zip(df.columns, lower_columns):
        if "id" in lower_col and id_col is None:
            id_col = original_col
            logger.debug(f"Identified 'id' column as '{id_col}'")
            break

    # Identify the 'sequence' column: first column containing 'sequence' in its name
    for original_col, lower_col in zip(df.columns, lower_columns):
        if "sequence" in lower_col and seq_col is None:
            seq_col = original_col
            logger.debug(f"Identified 'sequence' column as '{seq_col}'")
            break

    # Check if both columns were found
    if not id_col or not seq_col:
        missing = []
        if not id_col:
            missing.append("'id'")
        if not seq_col:
            missing.append("'sequence'")
        logger.warning(
            f"CSV file {file_path} does not contain required columns {', '.join(missing)}. Skipping."
        )
        return pd.DataFrame(columns=["id", "pep_seq"])

    # Add prefix to 'id'
    df["id"] = prefix + "_" + df[id_col].astype(str)

    # Rename sequence column to 'pep_seq' for consistency
    df = df.rename(columns={seq_col: "pep_seq"})

    # Select only the required columns
    return df[["id", "pep_seq"]]


def process_fasta(file_path, prefix, logger):
    """
    Process a FASTA file to extract 'id' and sequence, excluding entries with 'predicted' in the ID.

    Args:
        file_path (str): Path to the FASTA file.
        prefix (str): Prefix to add to each 'id'.
        logger (logging.Logger): Logger for logging messages.

    Returns:
        pd.DataFrame: DataFrame with 'id' and 'pep_seq' columns.
    """
    ids = []
    sequences = []
    excluded_count = 0
    total_records = 0

    try:
        # Open the FASTA file with UTF-8 encoding
        with open(file_path, "r", encoding="utf-8", errors="replace") as file:
            seq = ""
            id = None
            for line in file:
                if line.startswith(">"):
                    # If there's a previous record, save it if not excluded
                    if id is not None and "predicted" not in id.lower():
                        # Split by '|' and take the first part as ID
                        actual_id = id.split("|")[0].strip()
                        ids.append(f"{prefix}_{actual_id}")
                        sequences.append(seq)

                    elif id is not None:
                        # Increment excluded_count if previous record was excluded
                        excluded_count += 1

                    # Extract the new ID line
                    id_line = line[1:].strip()

                    # **Check if 'predicted' is in the ID before splitting**
                    if "predicted" in id_line.lower():
                        id = None
                        excluded_count += 1

                    else:
                        id = id_line

                    seq = ""
                    total_records += 1
                else:
                    seq += line.strip()

            # Append the last record if applicable
            if id is not None and seq:
                actual_id = id.split("|")[0].strip()
                ids.append(f"{prefix}_{actual_id}")
                sequences.append(seq)

            elif id is not None:
                excluded_count += 1

        logger.info(f"Successfully processed FASTA file: {file_path}")
        logger.info(f"Total records processed: {total_records}")
        logger.info(f"Total records excluded: {excluded_count}")
        logger.info(f"Total records added: {len(ids)}")
    except UnicodeDecodeError as e:
        logger.error(f"Unicode decode error reading FASTA file {file_path}: {e}")
        return pd.DataFrame(columns=["id", "pep_seq"])
    except Exception as e:
        logger.error(f"Error reading FASTA file {file_path}: {e}")
        return pd.DataFrame(columns=["id", "pep_seq"])

    # Create and return the DataFrame
    return pd.DataFrame({"id": ids, "pep_seq": sequences})
