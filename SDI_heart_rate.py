import os
import re

import pandas as pd
features = [
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
    create a df for a specific subject. takes its path, start, and end
    the output is a df size 21x7 for the relevant parameters
    """
    all_rows = []
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            all_rows.append(line.strip().split(','))

    feature_data = {}

    for row_idx in range(start_row, end_row + 1):
        row = all_rows[row_idx]
        feature_name = row[0].strip()

        values = []
        empty_count = 0

        for cell in row[1:]:
            cell = cell.strip()

            if cell == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                try:
                    values.append(float(cell))
                except:
                    values.append(None)

        feature_data[feature_name] = values

    df = pd.DataFrame(feature_data).T
    df.columns = [f"SAMPLE {i + 1}" for i in range(len(df.columns))]
    df.index.name = "Feature"
    return df

def safe_name(feature):
    """
    just creates a format that excel accepts (no ":" ect...)
    """
    # remove special characters and spaces
    return re.sub(r'[^0-9a-zA-Z_]', '_', feature)

def extract_feature_rows(df, features):
    """
    insert a df of subject and feature - and get it row
    """
    feature_rows = {}

    for f in features:
        key = safe_name(f)
        feature_rows[key] = df.loc[f].tolist()

    return feature_rows


if __name__ == "__main__":

    dir_path = "/Users/jasmineerell/Documents/Research/data/HR_SDI"
    output_file = os.path.join(dir_path, "HR_SDI_all_subjects_HRV_features.xlsx")

    # for each feature, we will collect rows from all subjects
    # dict: original_feature_name -> list of Series (one per subject)
    all_feature_rows = {f: [] for f in features}

    # scan csv files in dir
    for fname in os.listdir(dir_path):
        if not fname.endswith("_SDI.csv"):
            continue

        csv_file = os.path.join(dir_path, fname)

        # extract subject number from "number_SDI.csv"
        m = re.match(r'(\d+)_SDI\.csv$', fname)
        if not m:
            print(f"Skipping file (name does not match pattern 'number_SDI.csv'): {fname}")
            continue

        subj_number = m.group(1)
        subject_name = f"subject{subj_number}"

        # build df for this subject
        start, end = find_feature_row_range(csv_file)
        if start is None or end is None:
            print(f"Could not find feature rows in file: {fname}")
            continue

        df = create_features_dataframe(csv_file, start, end)
        subject_feature_rows = extract_feature_rows(df, features)

        # convert each list to a Series with index = sample columns, name = subject_name
        for feature in features:
            safe_f = safe_name(feature)
            if safe_f not in subject_feature_rows:
                print(f"Warning: feature '{feature}' not found for subject {subject_name} in file {fname}")
                continue

            values_list = subject_feature_rows[safe_f]
            row_series = pd.Series(values_list, index=df.columns, name=subject_name)
            all_feature_rows[feature].append(row_series)

    # write 1 excle file with 7 sheets -
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        for feature in features:
            rows_list = all_feature_rows[feature]
            if not rows_list:
                print(f"No data collected for feature '{feature}', skipping sheet.")
                continue

            # stack all subjects for this feature → DataFrame
            sheet_df = pd.DataFrame(rows_list)  # index = subject_name, columns = SAMPLE 1...N
            sheet_name = safe_name(feature)
            sheet_df.to_excel(writer, sheet_name=sheet_name, index=True)

    print(f"Excel file written to: {output_file}")



