from typing import List
import pandas as pd
import re

def extract_all_subjects_realtime_blocks(df):
    list_of_subjects = get_list_subjects_from_df(df)
    print(f"Meta data contains subjects - {', '.join(list_of_subjects)}")
    all_blocks = []
    for subject in list_of_subjects:
        subject_full_block = get_single_subject_all_blocks(df, subject)
        if not subject_full_block.empty:
            all_blocks.append(subject_full_block)
    return pd.concat(all_blocks, ignore_index=True) if all_blocks else pd.DataFrame()

def get_single_subject_all_blocks(df, subject):
    meetings = list_meetings_for_subjects(df, subject)
    all_blocks = []
    print(f"{subject} has {len(meetings)} meetings")

    for meeting in meetings:
        print(f"Adding meet {meeting}")
        sub_df = sub_df_for_specific_subject_meet(df, subject, meeting)
        # sub_df = sub_df[sub_df['subject'].astype(str).str.strip() == subject]  # filter subject
        block_df = get_segments(sub_df)

        if not block_df.empty:
            all_blocks.append(block_df)

    return pd.concat(all_blocks, ignore_index=True) if all_blocks else pd.DataFrame()

def list_meetings_for_subjects(df: pd.DataFrame, subject: str) -> list[int]:
    filtered = df[df['subject'].astype(str).str.strip() == subject]
    meets = (
        filtered['meet']
        .dropna()
        .astype(str)
        .str.extract(r'(\d+)')[0]
        .dropna()
        .astype(int)
        .unique()
    )
    return sorted(meets.tolist())

def sub_df_for_specific_subject_meet(df, subject, meeting_number):
    df_copy = df.copy()
    df_copy["__subject__"] = df_copy["subject"].astype(str).str.strip()
    df_copy["__meet_num__"] = (
        df_copy["meet"]
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype(float)
        .fillna(-1)
        .astype(int)
    )

    filtered = df_copy[(df_copy["__subject__"] == subject) & (df_copy["__meet_num__"] == meeting_number)]
    return filtered.drop(columns=["__subject__", "__meet_num__"]).reset_index(drop=True)

def get_segments(df: pd.DataFrame) -> pd.DataFrame:

    rt_blocks = []

    # scan every adjacent row pair for our two‐line header
    for i in range(len(df) - 1):
        # <-- START AT COL 4 to skip subject/meet/state/therapy -->
        row1 = df.iloc[i, 4 :].fillna("").astype(str).str.strip()
        row2 = df.iloc[i + 1, 4 :].fillna("").astype(str).str.strip()

        # detect header: first line has "Time", second has "(hh:mm:ss)"
        if row1.str.contains("Time", regex=False).any() and row2.str.contains(r"\(hh:mm:ss\)", regex=True).any():
            #build unique full header names by zipping row1 & row2
            seen = {}
            full_header = []
            for h1, h2 in zip(row1.tolist(), row2.tolist()):
                name = f"{h1} {h2}".strip()
                name = re.sub(r"\s+", " ", name)
                if name in seen:
                    seen[name] += 1
                    name = f"{name}.{seen[name]}"
                else:
                    seen[name] = 0
                full_header.append(name)

            # collect the numeric rows immediately after header
            data_rows = []
            time_idx = next(idx for idx, h in enumerate(full_header) if h.startswith("Time"))
            for j in range(i + 2, len(df)):
                cell = str(df.iat[j, 4 + time_idx]).strip()
                # stop when Time column no longer matches hh:mm:ss
                if not re.match(r"^\d{2}:\d{2}:\d{2}$", cell):
                    break
                data_rows.append(df.iloc[j, 4 :].tolist())

            if data_rows:
                block_df = pd.DataFrame(data_rows, columns=full_header)
                # prepend metadata columns in correct order
                block_df.insert(0, "therapy", df.iat[i, 3])
                block_df.insert(0,   "state", df.iat[i, 2])
                block_df.insert(0,    "meeting", df.iat[i, 1])
                block_df.insert(0,  "sub", df.iat[i, 0])
                rt_blocks.append(block_df)

    # combine all blocks (or return empty DF)
    return pd.concat(rt_blocks, ignore_index=True) if rt_blocks else pd.DataFrame()

def load_metadata_csv(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)

def get_list_subjects_from_df(df: pd.DataFrame) -> list:

    subjects = (
        df['subject']
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )
    return sorted(subjects)

def drop_empty_D_E(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a copy of df with columns 'D' and 'E' removed if they contain
    only NaN or empty-string values.
    """
    df_clean = df.copy()
    for col in [""]:
        if col in df_clean.columns:
            # build mask: True for NaN or blank-string
            empty_mask = df_clean[col].isna() | (df_clean[col].astype(str).str.strip() == "")
            if empty_mask.all():
                df_clean.drop(columns=[col], inplace=True)
    return df_clean

def create_block(path):
    big_df = pd.read_csv(path)
    # big_df.columns = big_df.columns.str.strip()
    real_time_df = extract_all_subjects_realtime_blocks(big_df)
    final_df = drop_empty_D_E(real_time_df)
    returned_path = path.replace(".csv", "_real_time_meta_data.csv")
    return returned_path, final_df.to_csv(returned_path, index=False)



