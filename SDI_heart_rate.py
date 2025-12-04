import os
import re
import pandas as pd

features =[
    "Sample limits (hh:mm:ss):",
    "Beats corrected (%):",
    "Effective data length (s):",
    "Mean RR  (ms):",
    "SDNN (ms):",
    "Mean HR (beats/min):",
    "SD HR (beats/min):",
    "Min HR (beats/min):",
    "Max HR (beats/min):",
    "RMSSD (ms):"
]

def find_feature_row_range(csv_file_path):
    """
    finds the index when the wanted feature starts and end, we will crop from it
    """
    start_row = None
    end_row = None

    with open(csv_file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            first_col = line.split(',')[0].strip().lower()

            if start_row is None and "mean rr" in first_col and "ms" in first_col:
                start_row = i

            if "rmssd" in first_col and "ms" in first_col:
                end_row = i

    return start_row, end_row

def create_features_dataframe(csv_file_path, start_row, end_row):
    """
    Create a df for a specific subject.

    - Includes all rows from start_row to end_row (Mean RR ... RMSSD),
    - PLUS the rows whose first column matches:
        * "Sample limits (hh:mm:ss):"
        * "Beats corrected (%):"
        * "Effective data length (s):"
      (matched in a case-insensitive way, without relying on fixed line numbers)

    """
    # Read all rows from the CSV
    all_rows = []
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            all_rows.append(line.strip().split(','))

    feature_data = {}



    # 1) indices for the standard HRV block (Mean RR ... RMSSD)
    row_indices = set(range(start_row, end_row + 1))

    # 2) find indices for the extra features by NAME, not line number
    for idx, row in enumerate(all_rows):
        if not row or not row[0].strip():
            continue

        first_col = row[0].strip()
        lc = first_col.lower()

        # Sample limits
        if "sample limits" in lc and "hh:mm:ss" in lc:
            row_indices.add(idx)

        # Beats corrected (%)
        elif "beats corrected" in lc and "%" in lc:
            row_indices.add(idx)

        # Effective data length
        elif "effective data length" in lc:
            row_indices.add(idx)

    # Sort to keep a stable, readable order
    row_indices = sorted(row_indices)


    for row_idx in row_indices:
        row = all_rows[row_idx]
        if not row:
            continue

        feature_name = row[0].strip()
        if not feature_name:
            continue

        values = []
        empty_count = 0

        for cell in row[1:]:
            cell = cell.strip()

            # Handle empty cells and stop after 2 consecutive empties
            if cell == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                continue

            # non-empty cell
            empty_count = 0

            # Detect interval pattern: e.g. "00:00:37-00:01:07"
            if "-" in cell and ":" in cell:
                # keep the interval as a string
                values.append(cell)
                continue

            # Try to parse as float
            try:
                num = float(cell)
                values.append(num)
            except ValueError:
                # Not numeric and not empty → keep as string
                values.append(cell)

        feature_data[feature_name] = values

    df = pd.DataFrame(feature_data).T
    df.columns = [f"SAMPLE {i + 1}" for i in range(len(df.columns))]
    df.index.name = "Feature"
    return df



def extract_feature_rows(df, features):
    """
    insert a df of subject and feature - and get it row
    """
    feature_rows = {}

    for f in features:
        key = safe_name(f)
        feature_rows[key] = df.loc[f].tolist()

    return feature_rows

def safe_name(feature):
    """
    just creates a format that excel accepts (no ":" ect...)
    """
    return re.sub(r'[^0-9a-zA-Z_]', '_', feature)


def build_excel_from_subject_features(dir_path, output_file, features):
    """
    Builds an Excel file with one sheet per feature.
    Each sheet contains one row per subject (values extracted from create_features_dataframe).
    """
    all_feature_rows = {f: [] for f in features}

    # scan CSVs in directory
    for fname in os.listdir(dir_path):
        if not fname.endswith(".csv"):
            continue

        csv_file = os.path.join(dir_path, fname)

        # extract subject number from "number_SDI.csv"
        m = re.match(r'.*_(\d+)\.csv$', fname)
        if not m:
            print(f"Skipping file (invalid name): {fname}")
            continue

        subj_number = m.group(1)
        subject_name = f"subject{subj_number}"

        # find feature block rows
        start, end = find_feature_row_range(csv_file)
        if start is None or end is None:
            print(f"Could not find HRV block in file: {fname}")
            continue

        # build df for this subject
        df = create_features_dataframe(csv_file, start, end)

        # collect each of the expected feature rows
        for feature in features:
            if feature not in df.index:
                print(f"Warning: feature '{feature}' missing in {fname}")
                continue

            row_values = df.loc[feature]
            row_values.name = subject_name  # store subject name as index
            all_feature_rows[feature].append(row_values)

    # write Excel - one sheet per feature
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        for feature in features:
            rows = all_feature_rows[feature]
            if not rows:
                print(f"No data for feature '{feature}', skipping sheet.")
                continue

            sheet_df = pd.DataFrame(rows)
            sheet_df.index.name = "Subject"

            sheet_name = safe_name(feature)
            sheet_df.to_excel(writer, sheet_name=sheet_name)

    print(f"Excel file created successfully: {output_file}")



if __name__ == "__main__":
    dir_path = "/Users/jasmineerell/Documents/Research/data/test"
    output_file = os.path.join(dir_path, "HR_SDI_all_subjects_HRV_features.xlsx")

    build_excel_from_subject_features(dir_path, output_file, features)

