"""
Utility functions for parsing and aggregating Rosetta docking score files.

This module provides tools for:
  - Reading score files with variable space-separated columns into pandas DataFrames,
  - Aggregating score files from multiple subfolders and tagging their origin,
  - Extracting the best (lowest-score) description from a score table.

Typical use case: You have a directory of experiment subfolders, each containing a
Rosetta score file (e.g. 'docking_scores.sc'). You want a single table with all results,
with each row labeled by subfolder, and a convenient way to select the best
complex per run.

Functions
---------
- read_and_convert(filepath)
    Reads a single score file into a DataFrame.
- get_optimal_clx(df)
    Returns the 'description' for the entry with the lowest 'total_score'.
- extract_score(dirpath, input_score_name)
    Aggregates all score files under a directory tree into a single DataFrame,
    adding an 'id' (subfolder) column and ensuring 'id' and 'description'
    are the leftmost columns.
"""

import re
import os
import pandas as pd


def read_and_convert(filepath):
    """
    Parse a Rosetta-style score file into a pandas DataFrame.

    Skips lines that start with 'SEQUENCE'. Handles variable whitespace. Converts
    columns to numeric where possible.

    :param filepath: The path to the score file to read.
    :type filepath: str
    :return: Parsed DataFrame with data from the file.
    :rtype: pandas.DataFrame
    :raises FileNotFoundError: If the file does not exist.
    :raises pd.errors.ParserError: If pandas cannot parse the file.
    :raises Exception: For other errors encountered during parsing.
    """
    try:
        with open(filepath, "r") as file:
            # Skip lines that start with 'SEQUENCE'
            lines = [line.strip() for line in file if not line.startswith("SEQUENCE")]

        data = [re.split(r"\s+", line.replace("SCORE: ", "").strip()) for line in lines]

        # Use first row as header, rest as data
        df = pd.DataFrame(data[1:], columns=data[0])

        # Convert numeric columns where possible
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except Exception:
                pass  # Keep as object if conversion fails

        return df
    except FileNotFoundError:
        print("The file was not found. Please check the filepath.")
    except pd.errors.ParserError:
        print("There was a problem parsing the file. Check the file's format.")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_optimal_clx(df):
    """
    Identify the entry with the lowest 'total_score' and return its 'description'.

    :param df: DataFrame with at least 'total_score' and 'description' columns.
    :type df: pandas.DataFrame
    :return: The 'description' corresponding to the lowest 'total_score',
    or None if not found.
    :rtype: str or None
    :raises ValueError: If the DataFrame does not contain the required columns.
    """
    try:
        if "total_score" not in df.columns or "description" not in df.columns:
            raise ValueError(
                "DataFrame must contain 'total_score' and 'description' columns."
            )
        idx = df["total_score"].idxmin()
        return df.loc[idx, "description"]
    except ValueError as ve:
        print(ve)
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def extract_score(dirpath, input_score_name="docking_scores.sc"):
    """
    Aggregate score files from subfolders into one DataFrame, labeling by subfolder.

    For each subfolder in `dirpath`, if a file named `input_score_name` exists,
    it is parsed and appended to a master DataFrame. Each row is tagged with an 'id'
    column set to the subfolder name. Columns are reordered to put 'id' and 'description'
    first if present.

    :param dirpath: Path to the parent directory containing subfolders with score files.
    :type dirpath: str
    :param input_score_name: Name of the score file in each subfolder
    (default: 'docking_scores.sc').
    :type input_score_name: str
    :return: DataFrame with all scores, 'id' and 'description' as the leftmost columns.
    :rtype: pandas.DataFrame

    Example
    -------
    >>> df = extract_score('experiments')
    >>> df.head()
    """
    all_rows = []
    for folder in os.listdir(dirpath):
        folder_path = os.path.join(dirpath, folder)
        score_file = os.path.join(folder_path, input_score_name)
        if os.path.isdir(folder_path) and os.path.isfile(score_file):
            try:
                df = read_and_convert(score_file)
                df.insert(0, "id", folder)
                all_rows.append(df)
            except Exception as e:
                print(f"Failed to read {score_file}: {e}")
    if not all_rows:
        return pd.DataFrame()
    df_all = pd.concat(all_rows, ignore_index=True)
    cols = df_all.columns.tolist()
    if "description" in cols:
        cols.insert(1, cols.pop(cols.index("description")))
        df_all = df_all[cols]
    return df_all
