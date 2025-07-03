import pandas as pd
from openpyxl import Workbook
from datetime import datetime
from pathlib import Path

# רשימת הפיצ'רים המדויקים (כולל רווחים ונקודתיים)
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
    " Geometric parameters         ",
    "  RR tri index:               ",
    "  TINN (ms):                  ",
    "  DC (ms):                    ",
    "  DCmod (ms):                 ",
    "  AC (ms):                    ",
    "  ACmod (ms):                 ",
    "Frequency-Domain Results      ",
    " Peak frequencies             ",
    "  VLF (Hz):                   ",
    "  LF (Hz):                    ",
    "  HF (Hz):                    ",
    " Absolute powers              ",
    "  VLF (ms^2):                 ",
    "  LF (ms^2):                  ",
    "  HF (ms^2):                  ",
    "  VLF (log):                  ",
    "  LF (log):                   ",
    "  HF (log):                   ",
    " Relative powers              ",
    "  VLF (%):                    ",
    "  LF (%):                     ",
    "  HF (%):                     ",
    " Normalized powers            ",
    "  LF (n.u.):                  ",
    "  HF (n.u.):                  ",
    "  Total power (ms^2):         ",
    " LF/HF ratio:                 ",
    " RESP (Hz):                   "
]

# תתי־כותרות שמופיעות בגיליון (אם מופיעות - נכניס לשורות)
SECTION_HEADERS = [
    " Geometric parameters         ",
    "Frequency-Domain Results      ",
    " Peak frequencies             ",
    " Absolute powers              ",
    " Relative powers              ",
    " Normalized powers            ",
    " Total power (ms^2):          ",
]

# פיצ'ר שיש לו שם אחר בקובץ המקורי (ולכן נחשב בנפרד)
RENAMED_FEATURES = {
    "  Sample limits (hh:mm:ss):   ": "  Time length (sec):          "
}

def parse_time_diff(time_str):
    try:
        start, end = time_str.split("-")
        fmt = "%H:%M:%S"
        delta = datetime.strptime(end.strip(), fmt) - datetime.strptime(start.strip(), fmt)
        return delta.total_seconds()
    except:
        return "Invalid"

def process_excel(input_path, output_path):
    xls = pd.ExcelFile(input_path)
    wb = Workbook()
    wb.remove(wb.active)

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        ws = wb.create_sheet(title=sheet_name)

        for state in ['baseline', 'recovery']:
            ws.append([state.upper()])
            ws.append(['Feature', 'Value'])

            # פילטר לפי מצב
            state_df = df[df['state'] == state]

            for _, row in state_df.iterrows():
                raw_feature = str(row['col1'])

                # תת כותרת
                if raw_feature in SECTION_HEADERS:
                    ws.append([raw_feature])
                    continue

                # טיפול בשם אחר: Sample limits → Time length
                if raw_feature in RENAMED_FEATURES:
                    value = row['col2']
                    seconds = parse_time_diff(value) if pd.notna(value) else "N/A"
                    ws.append([RENAMED_FEATURES[raw_feature], seconds])
                    continue

                # רק אם הפיצ'ר מופיע ב־ALLOWLIST
                if raw_feature in ALLOWED_FEATURES:
                    val1 = row['col2']
                    val2 = row['col3']
                    combined = val1 if pd.isna(val2) else f"{val1}, {val2}"
                    ws.append([raw_feature, combined])

            ws.append([])  # שורת רווח בין baseline ל-recovery

    wb.save(output_path)

def execute() :
# שימוש:
    folder_path = Path("C:/Users/97254/PycharmProjects/data-extraction/patients_excel")

#  לולאה על כל הקבצים בתיקייה עם סיומת xlsx
    for input_file in folder_path.glob("*.xlsx"):
    # יצירת שם הקובץ החדש עם הוספת "_cleaned" לפני הסיומת
        output_file = input_file.with_name(input_file.stem + "_cleaned" + input_file.suffix)
        process_excel(input_file, output_file)
