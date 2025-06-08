import pandas as pd

def read_csv_to_dataframe(csv_path: str) -> pd.DataFrame:
    """
    Reads a CSV file and returns it as a pandas DataFrame.

    Args:
        csv_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the CSV data.
    """
    try:
        df = pd.read_csv(csv_path)
        print("CSV read successfully. First few rows:")
        #print(df.head())
        return df
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return pd.DataFrame()


# Example usage:
# df = read_csv_to_dataframe("path/to/your/file.csv")

def createDataFrame(df):
    # Re-extract data to correctly begin from index 130 and end at first "NA" in the first data column
    # We use iloc directly to trim properly

    # Identify header again
    header_index = df[df.apply(lambda row: row.astype(str).str.contains("Time", case=False).any(), axis=1)].index[0]
    data_start = header_index + 1
    print(data_start)

    # Slice just the data chunk columns
    data_section = df.iloc[data_start:, 4:56].copy()
    data_section.columns = df.iloc[header_index, 4:56]

    # Find the first row where the first data column is "NA" and stop there
    first_col = data_section.columns[0]
    stop_index = data_section[data_section[first_col] == "NA"].index
    data_end = stop_index[0] if not stop_index.empty else len(data_section)
    data_trimmed = data_section.iloc[:data_end].copy()

    # Add identifying metadata columns
    #data_trimmed.insert(0, "state", current_state)
    #data_trimmed.insert(0, "meet", current_meet)
    #data_trimmed.insert(0, "subject", current_subject)

    df.to_csv("/Users/yuvalnadam/Desktop/CS/Cognition/MDMA/data-extraction/test/output.csv", index=False)


df = read_csv_to_dataframe("/Users/yuvalnadam/Desktop/CS/Cognition/MDMA/data-extraction/test/meta_data.csv")
createDataFrame(df)



