import pandas as pd
def find_feature_row_range(csv_file_path):
    """
    Finds the start and end row indices for HRV features.
    Returns: (start_row, end_row) as integers
    """
    start_row = None
    end_row = None

    with open(csv_file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            first_col = line.split(',')[0].strip().lower()

            # Find "Mean RR (ms)"
            if start_row is None and "mean rr" in first_col and "ms" in first_col:
                start_row = i

            # Find "RMSSD (ms)"
            if "rmssd" in first_col and "ms" in first_col:
                end_row = i

    return start_row, end_row


def create_features_dataframe(csv_file_path, start_row, end_row):
    """
    Creates a DataFrame with features from start_row to end_row (inclusive).
    Extracts columns until encountering two consecutive empty columns.
    Returns: DataFrame with features as rows and samples as columns
    """

    all_rows = []
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            row = line.strip().split(',')
            all_rows.append(row)

    # Extract the feature rows
    feature_data = {}

    for row_idx in range(start_row, end_row + 1):
        row = all_rows[row_idx]
        feature_name = row[0].strip()

        # Find where to stop: two consecutive empty columns - I GUESS IT WILL STAY THE SAME???
        values = []
        empty_count = 0

        for col_idx in range(1, len(row)):
            cell = row[col_idx].strip()

            if cell == '':
                empty_count += 1
                if empty_count >= 2:
                    # Found two consecutive empty columns, stop here
                    break
            else:
                empty_count = 0  # Reset counter
                # Try to convert to float
                try:
                    values.append(float(cell))
                except:
                    values.append(None)

        feature_data[feature_name] = values


    # Create DataFrame
    df = pd.DataFrame(feature_data).T
    df.columns = [f"SAMPLE {i + 1}" for i in range(len(df.columns))]
    df.index.name = "Feature"

    # Check if size is correct
    expected_shape = (7, 21)
    if df.shape != expected_shape:
        print(f"\n SOME DATA IS MISSING!")
        print(f"Expected: {expected_shape[0]} rows × {expected_shape[1]} columns")
        print(f"Got:      {df.shape[0]} rows × {df.shape[1]} columns")
    else:
        print(f"\n Data is complete: {df.shape[0]} rows × {df.shape[1]} columns")



    return df


if __name__ == "__main__":
    csv_file = "/Users/jasmineerell/Documents/Research/data/HR_SDI/Sub023_Session2_audio_ECG_hrv.csv"

    start, end = find_feature_row_range(csv_file)
    df = create_features_dataframe(csv_file, start, end)
    output_file = csv_file.replace('.csv', '_features.xlsx')
    df.to_excel(output_file)





