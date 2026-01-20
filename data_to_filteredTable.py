import os
import pandas as pd
import csv
import re
from pathlib import Path

# features
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

def process_file_final(file_path):
    parts = Path(file_path).parts
    subject, meet, state = parts[-4], parts[-3], parts[-2]
    filename = parts[-1]
    
    if "therapy" in state.lower():
        #fine name must be in the form of "...ECG_" followed by a letter 
        match = re.search(r'ECG_([A-Za-z])', filename)
        if match:
            letter = match.group(1).lower()
            state = f"therapy_{letter}"
        else:
            state = "therapy" # default

    extracted_data = []
    with open(file_path, newline='', encoding="utf-8") as f:
        reader = list(csv.reader(f))

    # global
    for row in reader:
        if len(row) < 2: continue
        feat = row[0]
        if feat in ALLOWED_FEATURES:
            extracted_data.append({
                "subject": subject, "meet": meet, "state": state,
                "type": "global", "col1": feat, "col2": row[1]
            })

    # segments
    for i, row in enumerate(reader):
        if len(row) >= 3 and "Time" in row[1] and "Beats total" in row[2]:
            headers, units = reader[i-1], reader[i]
            segment_idx = 1
            for data_row in reader[i+1:]:
                if not data_row or not str(data_row[1]).replace('.','',1).isdigit():
                    break
                
                for col_idx in range(3, len(data_row)):
                    feat_name = headers[col_idx].strip()
                    unit_name = units[col_idx].strip()
                    full_feat = f"{feat_name} {unit_name}"
                    
                    extracted_data.append({
                        "subject": subject, "meet": meet, "state": state,
                        "type": f"segment{segment_idx}", "col1": full_feat, "col2": data_row[col_idx]
                    })
                segment_idx += 1
            break
            
    return extracted_data

def generate_clean_metadata(root_folder, output_csv):
    all_rows = []
    print(f"Starting to process folders in: {root_folder}")
    
    for root, _, files in os.walk(root_folder):
        for file in files:
            #dont process meta data files
            if file.endswith(".csv") and "meta_data" not in file:
                all_rows.extend(process_file_final(os.path.join(root, file)))
    
    df = pd.DataFrame(all_rows)
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"Success! Created {output_csv} with {len(df)} rows.")

generate_clean_metadata("/Users/yuvalnadam/Desktop/CS/Cognition/data", "/Users/yuvalnadam/Desktop/CS/Cognition/data/filtered_meta_data.csv")