import pandas as pd
import csv
import os
import re

"Takes a directory with patients data, and creates in the same directory a meta_data.csv file"


def extract_metadata_from_filename(filename: str) -> dict:
    """
    Extracts subject, meet, state, and type from a filename.
    Expected formats:
      Sub15_Meet05_baseline_ECG_fixed_clean.csv
      Sub15_Meet05_therapy_ECG_A_clean.csv
      Sub15_Meet05_recovery_ECG_fixed_clean.csv
    Returns a dict with keys: subject, meet, state, type
    """
    base = os.path.splitext(filename)[0]  # strip .csv

    # Extract subject
    subject_match = re.search(r'(Sub\d+)', base, re.IGNORECASE)
    subject = subject_match.group(1) if subject_match else "unknown"

    # Extract meet
    meet_match = re.search(r'(Meet\d+a?)', base, re.IGNORECASE)
    meet = meet_match.group(1) if meet_match else "unknown"

    # Extract state (baseline / therapy / recovery)
    state_match = re.search(r'(baseline|therapy|recovery)', base, re.IGNORECASE)
    state = state_match.group(1).lower() if state_match else "unknown"

    # Extract type — only relevant for therapy files (ECG_A / B / C / D)
    type_value = extract_type_from_filename(filename) if state == "therapy" else ""

    return {"subject": subject, "meet": meet, "state": state, "type": type_value}


def preprocess(file_path: str) -> pd.DataFrame:
    """
    Reads a CSV file, replaces empty cells with 'NA', and adds 'subject', 'meet', 'state',
    and 'type' columns parsed from the filename. Pads short rows and returns a cleaned DataFrame.
    The metadata columns are moved to the front of the DataFrame.
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

    # Parse metadata from filename instead of directory structure
    fname = os.path.basename(file_path)
    meta = extract_metadata_from_filename(fname)

    df["subject"] = meta["subject"]
    df["meet"] = meta["meet"]
    df["state"] = meta["state"]
    df["type"] = meta["type"]

    # Move metadata columns to the front
    cols = ['subject', 'meet', 'state', 'type'] + [col for col in df.columns if col not in ['subject', 'meet', 'state', 'type']]
    df = df[cols]

    return df


def iterate_over_drive(root: str) -> pd.DataFrame:
    """
    Recursively finds all .csv files under the root, processes them using preprocess(),
    and returns a single concatenated DataFrame.
    Expected hierarchy: root/ -> subject/ -> meet/ -> *.csv
    """
    meet_dir_re = re.compile(r'^meet\s*\d+a?$', re.IGNORECASE)

    dfs = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirname = os.path.basename(dirpath).strip()

        # Skip directories that look like they should be meet folders but have invalid names
        if dirname.lower().startswith('meet') and not meet_dir_re.match(dirname):
            print(f"[INFO] Skipping directory '{dirpath}': invalid 'meet' format")
            continue

        for fname in filenames:
            if fname.lower().endswith(".csv") and "meta_data" not in fname.lower():
                file_path = os.path.join(dirpath, fname)

                # Warn if filename doesn't contain expected state keyword
                if not re.search(r'(baseline|therapy|recovery)', fname, re.IGNORECASE):
                    print(f"[WARNING] Could not detect state in filename: '{fname}' — skipping")
                    continue

                try:
                    df = preprocess(file_path)
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


if __name__ == "__main__":
    data_path = "/Users/jasmineerell/Documents/CS-second-year/MDMA/data-2026"
    metaDataCsvCreator(data_path)