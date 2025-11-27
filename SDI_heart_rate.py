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

    csv_file = "/Users/jasmineerell/Documents/Research/data/HR_SDI/Sub023_Session2_audio_ECG_hrv.csv"
    subject_id = "23"
    start, end = find_feature_row_range(csv_file)
    df = create_features_dataframe(csv_file, start, end)
    rows = extract_feature_rows(df, features)


    output_file = f"/Users/jasmineerell/Documents/Research/data/HR_SDI/Sub{subject_id}_HRV_features.xlsx"

    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        for feature in features:
            if feature not in df.index:
                print(f"Warning: feature '{feature}' not found in DataFrame index")
                continue

            # 1xN DataFrame: keep as row
            row_df = df.loc[[feature]]  # using list keeps it as a DataFrame (not Series)

            sheet_name = safe_name(feature)
            row_df.to_excel(writer, sheet_name=sheet_name, index=True)

    print(f"Excel file written to: {output_file}")



