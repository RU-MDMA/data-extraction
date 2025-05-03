import os
import csv
import pandas as pd

def read_csv_fill_NA(path, delimiter=",", show_headers=True):
    """
    Reads a CSV file, replaces empty cells with 'NA', and returns a pandas DataFrame.
    Pads short rows to match the longest one. Optionally prints without index/headers.
    """
    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delimiter)
        rows = []
        max_cols = 0
        for row in reader:
            cleaned_row = [cell if cell.strip() != "" else "NA" for cell in row]
            rows.append(cleaned_row)
            max_cols = max(max_cols, len(cleaned_row))

    # Pad all rows to same length
    padded = [r + ["NA"] * (max_cols - len(r)) for r in rows]
    
    # Generate generic column names
    col_names = [f"col{i+1}" for i in range(max_cols)]
    
    # Create DataFrame
    df = pd.DataFrame(padded, columns=col_names)
    return df

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
                try:
                    df = read_csv_fill_NA(file_path)
                    dfs.append(df)
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")

    if not dfs:
        print("No CSV files found under", root)
        return None

    # Combine all into one DataFrame
    combined = pd.concat(dfs, ignore_index=True)
    out_path = os.path.join(root, "meta_data.csv")
    combined.to_csv(out_path, index=False)
    print(f"Combined DataFrame written to {out_path}")
    return combined

# Update this to the folder you want to scan
root_drive = r"./subject 15"
iterate_over_drive(root_drive)