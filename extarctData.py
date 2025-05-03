import os
import pandas as pd
import ace_tools as tools


root_drive = "./subject_15/"  
output_file_path = "./combined_data.csv"

target_subdirs = {"baseline", "recovery"}
expected_meetings = [f"meet {i}" for i in range(1, 18)]

#subject --> meeting --> base\ther\reco --> csv

def iterate_over_drive(root_drive, output_file_path, target_subdirs):
    """
    Iterrate over a given directory path and appends any .csv
    Args:
        path (str): Path to the root directory.        

    """
    df = pd.DataFrame()

    # Walk through the file system
    for dirpath, _, filenames in os.walk(root_drive):
        current_folder = os.path.basename(dirpath).lower()
        if current_folder in target_subdirs: #to handle the name
            for filename in filenames:
                if filename.lower().endswith(".csv"):
                    file_path = os.path.join(dirpath, filename)
                    df_file = read_csv_fill_MA(file_path)
                    df = pd.concat([df, df_file], ignore_index=True)


    df.to_csv(output_file_path, index=False)
    print(df)
    print(f"\nCombined CSV saved to {output_file_path}")

def read_csv_fill_MA(path, delimiter=':'):
    """
    Reads a CSV with irregular row lengths and returns a DataFrame
    padding missing values with the string "MA".
    
    Args:
        path (str): Path to the CSV file.
        delimiter (str): Field delimiter (default is comma).
        
    Returns:
        pd.DataFrame: DataFrame with uniform columns and "MA" for missing cells.
    """
    # Read all rows
    with open(path, newline='') as f:
        reader = csv.reader(f, delimiter=delimiter)
        rows = [row for row in reader]
    
    # Determine the maximum number of columns
    max_cols = max(len(r) for r in rows)
    
    # Pad each row with "MA" where fields are missing
    padded = [r + ["MA"] * (max_cols - len(r)) for r in rows]
    
    # Generate generic column names: col1, col2, ..., colN
    col_names = [f"col{i+1}" for i in range(max_cols)]
    
    # Build DataFrame
    df = pd.DataFrame(padded, columns=col_names)
    return df

iterate_over_drive(root_drive, output_file_path, target_subdirs)


    
   

