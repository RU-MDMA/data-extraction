import pandas as pd

def find_feature_row_range(csv_file_path):
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


def get_row(df, feature):
    try:
        return df.loc[feature].tolist()
    except KeyError:
        return None



if __name__ == "__main__":

    # ----------- READ SUBJECT FILE & BUILD DF ------------
    csv_file = "/Users/jasmineerell/Documents/Research/data/HR_SDI/Sub023_Session2_audio_ECG_hrv.csv"
    subject_id = "23"

    start, end = find_feature_row_range(csv_file)
    df = create_features_dataframe(csv_file, start, end)
    row = get_row(df, "Mean RR  (ms):")
    print(row)

