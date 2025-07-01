import pandas as pd
from pathlib import Path
from datetime import datetime

ALLOWED_FEATURES = [
    "  Beats corrected (%):        ",
    "  Time length (sec):          ",
    "  Mean RR  (ms):              ",
    "  SDNN (ms):                  ",
    "  Mean HR (beats/min):        ",
    "  SD HR (beats/min):          ",
    "  Min HR (beats/min):         ",
    "  Max HR (beats/min):         ",
    "  RMSSD (ms):                 ",
    "  NNxx (beats):               ",
    "  pNNxx (%):                  ",
    "  SDANN (ms):                 ",
    "  SDNN index (ms):            ",
    "  RR tri index:               ",
    "  TINN (ms):                  ",
    "  DC (ms):                    ",
    "  DCmod (ms):                 ",
    "  AC (ms):                    ",
    "  ACmod (ms):                 ",
    "  VLF (Hz):                   ",
    "  LF (Hz):                    ",
    "  HF (Hz):                    ",
    "  VLF (ms^2):                 ",
    "  LF (ms^2):                  ",
    "  HF (ms^2):                  ",
    "  VLF (log):                  ",
    "  LF (log):                   ",
    "  HF (log):                   ",
    "  VLF (%):                    ",
    "  LF (%):                     ",
    "  HF (%):                     ",
    "  LF (n.u.):                  ",
    "  HF (n.u.):                  ",
    " LF/HF ratio:                 ",
    " RESP (Hz):                   "
]

RENAMED_FEATURES = {
    "  Sample limits (hh:mm:ss):   ": "  Time length (sec):          "
}

SEGMENT_FEATURES = [
    "Beats corrected",
    "Mean RR",
    "SDNN",
    "Mean HR",
    "RMSSD",
    "VLF power",
    "LF power",
    "HF power",
    "LF/HF ratio",
    "RESP"
]

def parse_time_duration(time_str):
    try:
        start_str, end_str = time_str.split("-")
        t1 = datetime.strptime(start_str.strip(), "%H:%M:%S")
        t2 = datetime.strptime(end_str.strip(), "%H:%M:%S")
        delta = t2 - t1
        return round(delta.total_seconds(), 2)
    except:
        return None

def process_meta_data(file_path):
    input_path = Path(file_path)
    df = pd.read_csv(file_path)
    combined_rows = []
    i = 0
    total_rows = len(df)

    while i < total_rows:
        segment_mode = False
        header_row = None
        col_map = {}
        segment_index = 1

        # שלב 1: עיבוד הגלובלי
        while i < total_rows:
            row = df.iloc[i]

            if str(row.get("col2")).strip() == "Time" and str(row.get("col3")).strip() == "Beats total":
                header_row = row
                segment_mode = True
                i += 1
                break

            if row.get("col1") in ALLOWED_FEATURES or row.get("col1") in RENAMED_FEATURES:
                row_data = row.iloc[:5].copy()
                raw_feature = row_data["col1"]
                renamed = RENAMED_FEATURES.get(raw_feature, raw_feature)
                row_data["col1"] = renamed
                if raw_feature in RENAMED_FEATURES and renamed == "  Time length (sec):          ":
                    time_str = str(row_data["col2"])
                    duration = parse_time_duration(time_str)
                    row_data["col2"] = duration

                reordered = {
                    "subject": row_data["subject"],
                    "meet": row_data["meet"],
                    "state": row_data["state"],
                    "type": "global",
                    "col1": row_data["col1"],
                    "col2": row_data["col2"]
                }
                combined_rows.append(reordered)

            i += 1

        # שלב 2: עיבוד הסגמנטים
        if segment_mode and header_row is not None:
            units_row = df.iloc[i] if i < total_rows else None
            i += 1

            # מיפוי תכונה -> עמודה
            col_map = {}
            for col in df.columns:
                header_value = str(header_row[col]).strip()
                if header_value.strip() in SEGMENT_FEATURES:
                    unit = str(units_row[col]).strip()
                    if "(n.u.)" in unit or "(count)" in unit.lower():
                        continue
                    feature_with_unit = f"{header_value.strip()} {unit}" if unit else header_value.strip()
                    col_map[feature_with_unit] = col

            # עיבוד השורות של הסגמנטים
            while i < total_rows:
                row = df.iloc[i]
                val = str(row.get("col3")).strip()
                if not val.replace('.', '', 1).isdigit():
                    break

                for feature_with_unit, col in col_map.items():
                    combined_rows.append({
                        "subject": row["subject"],
                        "meet": row["meet"],
                        "state": row["state"],
                        "type": f"segment{segment_index}",
                        "col1": feature_with_unit,
                        "col2": row[col]
                    })

                segment_index += 1
                i += 1

            while i < total_rows:
                row = df.iloc[i]
                if row.get("col1") in ALLOWED_FEATURES or row.get("col1") in RENAMED_FEATURES or (
                        str(row.get("col2")).strip() == "Time" and str(row.get("col3")).strip() == "Beats total"):
                    break
                i += 1

    # כתיבת קובץ הפלט
    df_combined = pd.DataFrame(combined_rows)
    output_path = input_path.parent / "filtered_meta_data.csv"
    df_combined.to_csv(output_path, index=False, encoding='utf-8')
