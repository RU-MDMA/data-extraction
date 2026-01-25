import os
import pandas as pd
import csv
import re
from pathlib import Path

#list of features
ALLOWED_FEATURES = [
    "  Beats corrected (%):        ", "  Time length (sec):          ",
    "  Mean RR  (ms):              ", "  SDNN (ms):                  ",
    "  Mean HR (beats/min):        ", "  SD HR (beats/min):          ",
    "  Min HR (beats/min):         ", "  Max HR (beats/min):         ",
    "  RMSSD (ms):                 ", "  NNxx (beats):               ",
    "  pNNxx (%):                  ", "  SDANN (ms):                 ",
    "  SDNN index (ms):            ", "  RR tri index:               ",
    "  TINN (ms):                  ", "  DC (ms):                    ",
    "  DCmod (ms):                 ", "  AC (ms):                    ",
    "  ACmod (ms):                 ", "  VLF (Hz):                   ",
    "  LF (Hz):                    ", "  HF (Hz):                    ",
    "  VLF (ms^2):                 ", "  LF (ms^2):                  ",
    "  HF (ms^2):                  ", "  VLF (log):                  ",
    "  LF (log):                   ", "  HF (log):                   ",
    "  VLF (%):                    ", "  LF (%):                     ",
    "  HF (%):                     ", "  LF (n.u.):                  ",
    "  HF (n.u.):                  ", "  Total power (ms^2):         ",
    " LF/HF ratio:                 ", " RESP (Hz):                   "
]

def process_file_global_only(file_path):
    parts = Path(file_path).parts
    subject, meet, state = parts[-4], parts[-3], parts[-2]
    filename = parts[-1]
    
    # therapy A B C D 
    if "therapy" in state.lower():
        match = re.search(r'ECG_([A-Z])', filename)
        state = f"therapy_{match.group(1).lower()}" if match else "therapy"

    extracted_rows = []
    try:
        with open(file_path, newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 2: continue
                feat_name = row[0]
                if feat_name in ALLOWED_FEATURES:
                    extracted_rows.append({
                        "subject": subject,
                        "meet": meet,
                        "state": state,
                        "type": "global",
                        "col1": feat_name,
                        "col2": row[1]
                    })
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        
    return extracted_rows

def generate_global_metadata(root_folder, output_csv):
    all_data = []
    print(f"Starting to process global data from: {root_folder}")
    
    for root, _, files in os.walk(root_folder):
        for file in files:
            if file.endswith(".csv") and "meta_data" not in file.lower():
                all_data.extend(process_file_global_only(os.path.join(root, file)))
    
    if not all_data:
        print("No data found!")
        return

    df = pd.DataFrame(all_data)
    
    df = df.drop_duplicates()
    
    df = df.sort_values(by=['subject', 'meet', 'state'])
    
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    
    print(f"\n--- Process Complete ---")
    print(f"File saved as: {output_csv}")
    print(f"Total rows: {len(df)}")
    print(f"Subjects included: {df['subject'].nunique()}")

root_dir = "/Users/yuvalnadam/Desktop/CS/Cognition/data"
output_file = "/Users/yuvalnadam/Desktop/CS/Cognition/data/ans_global_metadata.csv"
generate_global_metadata(root_dir, output_file)