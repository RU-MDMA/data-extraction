import pandas as pd
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

# שמות אלטרנטיביים שיש להמיר (כמו Sample limits)
RENAMED_FEATURES = {
    "  Sample limits (hh:mm:ss):   ": "  Time length (sec):          "
}


def filter_metadata(input_csv_path):
    # הפיכת הנתיב לאובייקט Path
    input_path = Path(input_csv_path)

    # קריאת הקובץ
    df = pd.read_csv(input_path)

    # סט של פיצ'רים לשימור
    all_features_to_keep = set(ALLOWED_FEATURES) | set(RENAMED_FEATURES.keys())

    # סינון לפי ערכים ב-col1
    filtered_df = df[df['col1'].isin(all_features_to_keep)]

    # שמירת 6 העמודות הראשונות
    filtered_df = filtered_df.iloc[:, :6]

    # יצירת נתיב חדש לאותו תיק
    output_path = input_path.parent / "filtered_meta_data.csv"

    # שמירה
    filtered_df.to_csv(output_path, index=False, encoding='utf-8')