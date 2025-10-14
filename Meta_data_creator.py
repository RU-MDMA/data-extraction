import pandas as pd
import csv
import os
import re


def preprocess(file_path: str, type_value: str = "") -> pd.DataFrame:
    """
    Reads a CSV file, replaces empty cells with 'NA', and adds 'subject', 'meet', and 'state' columns
    based on the file path. Pads short rows and returns a cleaned DataFrame.
    The 'subject', 'meet', and 'state' columns are moved to the front of the DataFrame.
    """
    with open(file_path, newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = []
        max_cols = 0
        for row in reader:
            cleaned_row = [cell if cell.strip() != "" else "NA" for cell in row]
            rows.append(cleaned_row)
            max_cols = max(max_cols, len(cleaned_row))

    # Pad all rows to match the maximum column length
    padded = [r + ["NA"] * (max_cols - len(r)) for r in rows]

    # Add column names
    col_names = [f"col{i + 1}" for i in range(max_cols)]
    df = pd.DataFrame(padded, columns=col_names)

    # Add metadata from the file path
    parts = os.path.normpath(file_path).split(os.sep)
    if len(parts) >= 4:
        subject, meet, state = parts[-4], parts[-3], parts[-2]
    else:
        subject = meet = state = "unknown"

    df["subject"] = subject
    df["meet"] = meet
    df["state"] = state
    df["type"] = type_value  # Add the passed-in type

    # Move 'subject', 'meet', and 'state' to the front
    cols = ['subject', 'meet', 'state', 'type'] + [col for col in df.columns if col not in ['subject', 'meet', 'state', 'type']]
    df = df[cols]

    return df


def iterate_over_drive(root: str) -> pd.DataFrame:
    """
    Recursively finds all .csv files under the root, processes them using preprocess(),
    and returns a single concatenated DataFrame.
    """
    meet_dir_re = re.compile(r'^\s*meet\s+\d+a?\s*$', re.IGNORECASE)

    dfs = []
    for dirpath, _, filenames in os.walk(root):
        dirname = os.path.basename(dirpath)

        if dirname.lower().startswith('meet') and not meet_dir_re.match(dirname):
            print(f"[INFO] Skipping directory '{dirpath}': invalid 'meet' format")
            continue

        for fname in filenames:
            if fname.lower().endswith(".csv") and "meta_data" not in fname.lower():
                file_path = os.path.join(dirpath, fname)

                # Determine 'state' from folder structure
                parts = os.path.normpath(file_path).split(os.sep)
                state = parts[-2] if len(parts) >= 2 else "unknown"

                # Extract type if state is therapy
                type_value = extract_type_from_filename(fname) if state.lower() == "therapy" else ""

                try:
                    df = preprocess(file_path, type_value=type_value)
                    dfs.append(df)
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")

    if not dfs:
        print(f"No CSV files found under {root}")
        return None

    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df


def extract_type_from_filename(filename):
    match = re.search(r'ECG_([A-Z])', filename, re.IGNORECASE)
    return match.group(1).upper() if match else ""



def metaDataCsvCreator(root_path: str):
    """
    Creates a combined metadata CSV file from all CSVs in the root_path directory.
    """
    combined_df = iterate_over_drive(root_path)
    if combined_df is not None:
        out_path = os.path.join(root_path, "meta_data.csv")
        combined_df.to_csv(out_path, index=False)
        return out_path
    else:
        return None






