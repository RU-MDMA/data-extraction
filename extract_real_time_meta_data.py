import pandas as pd

def extract_subject_realtime_data(file_path: str, subject_filter: str = "subject 16") -> pd.DataFrame:
    # Load the file
    df = pd.read_csv(file_path)

    # Locate the header rows: search for row containing 'Time' and next one with '(hh:mm:ss)'
    for i in range(len(df) - 1):
        header1 = df.iloc[i, 3:].fillna("").astype(str).str.strip()
        header2 = df.iloc[i + 1, 3:].fillna("").astype(str).str.strip()

        if "Time" in header1.values.tolist() and "(hh:mm:ss)" in header2.values.tolist():
            data_start_index = i + 2  # actual data begins here
            break
    else:
        raise ValueError("Real-time data headers not found in the file.")

    # Combine headers
    full_header = (header1 + " " + header2).str.replace(" +", " ", regex=True).str.strip()

    # Extract subject info from metadata columns
    subject_info = df.loc[i, ['subject', 'meet', 'state']].values.tolist()

    # Read data rows until the next fully NaN row
    data_rows = []
    for j in range(data_start_index, len(df)):
        row = df.iloc[j, 3:]
        if row.isna().all():
            break
        data_rows.append(row.tolist())

    # Build DataFrame
    result_df = pd.DataFrame(data_rows, columns=full_header)
    result_df.insert(0, "subject", subject_info[0])
    result_df.insert(1, "meet", subject_info[1])
    result_df.insert(2, "state", subject_info[2])

    # Filter for subject 16 if requested
    if subject_filter:
        result_df = result_df[result_df["subject"].str.strip().eq(subject_filter)]

    return result_df.reset_index(drop=True)


path = "/Users/jasmineerell/Documents/CS-second-year/MDMA/data/meta_data.csv"
df_subject16 = extract_subject_realtime_data(path, subject_filter="subject 16")
print(df_subject16.head())
