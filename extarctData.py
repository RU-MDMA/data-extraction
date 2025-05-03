import os
import pandas as pd

root_drive = ""  
output_file_path = "combined_data.csv"

target_subdirs = {"baseline", "recovery"}
expected_meetings = [f"meet {i}" for i in range(1, 18)]

df_list = []

#subject --> meeting --> base\ther\reco --> csv

for dirpath, _, filenames in os.walk(root_drive):
    current_folder = os.path.basename(dirpath).lower()
    if current_folder in target_subdirs: #to handle the name 
        for filename in filenames:
            if filename.lower().endswith(".csv"):
                file_path = os.path.join(dirpath, filename)
                try:
                    df = pd.read_csv(file_path)
                    
                    print(f"Loaded: {file_path}")
                except Exception as e:
                    print(f"Failed to read {file_path}: {e}")

if df_list:
    combined_df = pd.concat(df_list, ignore_index=True)
    combined_df.to_csv(output_file_path, index=False)
    print(f"\nCombined CSV saved to {output_file_path}")
else:
    print("No CSV files found in the specified folders.")

