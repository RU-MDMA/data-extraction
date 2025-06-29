from typing import List
import pandas as pd

def extract_all_subjects_realtime_blocks(df):
    list_of_subjects = list_subjects_from_df(df)
    print(f"Meta data contains subjects - {', '.join(list_of_subjects)}")
    all_blocks = []
    for subject in list_of_subjects:
        subject_full_block = extract_single_subject_blocks(df, subject)
        if not subject_full_block.empty:
            all_blocks.append(subject_full_block)
    return pd.concat(all_blocks, ignore_index=True) if all_blocks else pd.DataFrame()

def extract_single_subject_blocks(df: pd.DataFrame, subject: str) -> pd.DataFrame:
    meetings = list_meetings_for_subjects(df, subject)
    all_blocks = []
    print(f"{subject} has {len(meetings)} meetings")

    for meeting in meetings:
        print(f"Adding meet {meeting}")
        sub_df = sub_data_frame_for_meet(df, subject, meeting)
        sub_df = sub_df[sub_df['subject'].astype(str).str.strip() == subject]  # filter subject
        block_df = extract_real_time_block(sub_df)

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

def sub_data_frame_for_meet(df: pd.DataFrame, subject: str, meeting_number: int) -> pd.DataFrame:

    df_copy = df.copy()

    # Normalize subject field
    df_copy["__subject__"] = df_copy["subject"].astype(str).str.strip()

    # Normalize meeting number field
    df_copy["__meet_num__"] = (
        df_copy["meet"]
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype(float)
        .fillna(-1)
        .astype(int)
    )

    filtered = df_copy[
        (df_copy["__subject__"] == subject) &
        (df_copy["__meet_num__"] == meeting_number)
    ]

    return filtered.drop(columns=["__subject__", "__meet_num__"]).reset_index(drop=True)


def extract_real_time_block(df: pd.DataFrame) -> pd.DataFrame:

    rt_blocks = []

    for i in range(len(df) - 1):
        row1 = df.iloc[i, 3:].fillna("").astype(str).str.strip()
        row2 = df.iloc[i + 1, 3:].fillna("").astype(str).str.strip()

        if "Time" in row1.values.tolist() and "(hh:mm:ss)" in row2.values.tolist():
            full_header = (row1 + " " + row2).str.replace(" +", " ", regex=True).str.strip()

            # Extract data rows until a blank line
            data_rows = []
            for j in range(i + 2, len(df)):
                row = df.iloc[j, 3:]
                if row.isna().all():
                    break
                data_rows.append(row.tolist())

            if data_rows:
                block_df = pd.DataFrame(data_rows, columns=full_header)
                block_df.insert(0, "subject", df.loc[i, "subject"])
                block_df.insert(1, "meet", df.loc[i, "meet"])
                block_df.insert(2, "state", df.loc[i, "state"])
                rt_blocks.append(block_df)

    return pd.concat(rt_blocks, ignore_index=True) if rt_blocks else pd.DataFrame()

def load_metadata_csv(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)

def list_subjects_from_df(df: pd.DataFrame) -> list:

    subjects = (
        df['subject']
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )
    return sorted(subjects)

def real_time_meta_data(path):
    big_df = pd.read_csv(path)
    real_time_df = extract_all_subjects_realtime_blocks(big_df)
    returned_path = path.replace(".csv", "_real_time_meta_data.csv")
    return returned_path, real_time_df.to_csv(returned_path, index=False)


