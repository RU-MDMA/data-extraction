import os
import csv
import pandas as pd

def add_column_names(data_rows, max_cols):
    """
    Add generic column names to the data and return a DataFrame.
    """
    col_names = [f"col{i+1}" for i in range(max_cols)]
    return pd.DataFrame(data_rows, columns=col_names)

def read_csv_fill_NA(path, delimiter=","):
    """
    Reads a CSV file, replaces empty cells with 'NA', and returns a DataFrame.
    Pads short rows to the max number of columns found in the file.
    """
    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delimiter)
        rows = []
        max_cols = 0
        for row in reader:
            cleaned_row = [cell if cell.strip() != "" else "NA" for cell in row]
            rows.append(cleaned_row)
            max_cols = max(max_cols, len(cleaned_row))

    # Pad all rows
    padded = [r + ["NA"] * (max_cols - len(r)) for r in rows]
    
    return add_column_names(padded, max_cols)

def iterate_over_drive(root):
    """
    Recursively finds all .csv files under root, cleans each,
    and returns a single concatenated DataFrame.
    """
    dfs = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:

            if fname.lower().endswith(".csv"):
                file_path = os.path.join(dirpath, fname)
                if "therapy" not in file_path.lower():
                    try:
                        df = read_csv_fill_NA(file_path)
                        df = extract_metadata(df, str(file_path))
                        dfs.append(df)
                    except Exception as e:
                        print(f"Failed to process {file_path}: {e}")

    if not dfs:
        print("No CSV files found under", root)
        return None

    # Combine all into one DataFrame
    combined = pd.concat(dfs, ignore_index=True)
    print(combined)
    return combined

def extract_metadata(df: pd.DataFrame, file_path: str) -> pd.DataFrame:
    """
    Adds 'subject', 'meet', and 'state' columns to df by parsing
    the last three folders in file_path. E.g.:

        .../subject 15/meet 1/baseline/filename.csv

    Args:
        df:         pandas DataFrame to enrich
        file_path: full path to the CSV file

    Returns:
        A new DataFrame with 'subject', 'meet', 'state' columns appended.
    """
    parts = os.path.normpath(file_path).split(os.sep)
    # We expect at least 4 components: [..., subject, meet, state, filename]
    if len(parts) >= 4:
        subject, meet, state = parts[-4], parts[-3], parts[-2]
    else:
        subject = meet = state = "unknown"

    out = df.copy()
    out["subject"] = subject
    out["meet"]    = meet
    out["state"]   = state
    return out

def main():
    # Update this to the folder you want to scan
    root_drive = r"C:\Users\jasminee\MDMA\RU-MDMA\test\subject 15"
    combined = iterate_over_drive(root_drive)
    out_path = os.path.join(root_drive, "meta_data.csv")
    combined.to_csv(out_path, index=False)
    print(f"Combined DataFrame written to {out_path}")

main()
