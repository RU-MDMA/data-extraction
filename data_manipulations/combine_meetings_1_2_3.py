import pandas as pd
import numpy as np

COMBINED_LABEL = "meet 1-3 median"   # ASCII only for Excel readability

def extract_meeting_num(s: pd.Series) -> pd.Series:
    return s.astype(str).str.extract(r"(\d+)", expand=False).astype("Int64")

def get_first_not_na_val(series: pd.Series):
    nonnull = series.dropna()
    return nonnull.iat[0] if not nonnull.empty else np.nan

def combine_meetings_1_3_block(block: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a 'block' DataFrame, combines meetings 1–3 into a single
    median meeting per (sub, state, sample_idx), removes the original
    meetings 1–3, and returns the updated DataFrame.
    """
    # Work on a copy so we don't mutate the caller's DataFrame
    df = block.copy()

    # --- meeting index extraction ---
    df["meeting_num"] = extract_meeting_num(df["meeting"])

    # Time column for within-meeting ordering (if exists)
    time_col = next((c for c in ["Time (hh:mm:ss)", "time", "Time"] if c in df.columns), None)
    if time_col:
        df["_sort_key"] = pd.to_timedelta(df[time_col].astype(str), errors="coerce").dt.total_seconds()
    else:
        df["_sort_key"] = np.arange(len(df))

    # Split to "keep as is" and "meetings 1–3"
    df_keep = df[~df["meeting_num"].isin([1, 2, 3])].copy()
    df_123  = df[df["meeting_num"].isin([1, 2, 3])].copy()

    # Grouping axes (subject, optionally state)
    group_axes = ["sub"]
    if "state" in df_123.columns:
        group_axes.append("state")

    # Assign sample index within (sub, state, meeting)
    df_123 = df_123.sort_values(group_axes + ["meeting_num", "_sort_key"])
    df_123["sample_idx"] = df_123.groupby(group_axes + ["meeting_num"]).cumcount() + 1

    # === Numeric medians per (sub, state, sample_idx) ===
    numeric_cols = df_123.select_dtypes(include="number").columns.tolist()
    for helper in ["meeting_num", "_sort_key"]:
        if helper in numeric_cols:
            numeric_cols.remove(helper)

    med_numeric = (
        df_123.groupby(group_axes + ["sample_idx"], as_index=False)[numeric_cols]
              .median()
    )

    # === Non-numeric columns (representative value) ===
    non_numeric_cols = [c for c in df_123.columns if c not in numeric_cols]
    for drop in ["meeting_num", "_sort_key"]:
        if drop in non_numeric_cols:
            non_numeric_cols.remove(drop)

    rep_non_numeric = (
        df_123.groupby(group_axes + ["sample_idx"], as_index=False)[non_numeric_cols]
              .agg(get_first_not_na_val)
    )

    # === Merge numeric + non-numeric ===
    combined = pd.merge(
        rep_non_numeric,
        med_numeric,
        on=group_axes + ["sample_idx"],
        how="left"
    )

    # Mark as combined meeting
    combined["meeting"] = COMBINED_LABEL

    # Drop helper columns
    combined.drop(columns=["sample_idx", "meeting_num", "_sort_key"],
                  inplace=True, errors="ignore")
    df_keep.drop(columns=["meeting_num", "_sort_key"],
                 inplace=True, errors="ignore")

    # Re-align column order to original
    final_cols = [c for c in df.columns if c in combined.columns]
    combined = combined.reindex(columns=final_cols)
    df_keep  = df_keep.reindex(columns=final_cols)

    # Concatenate kept meetings + combined 1–3
    df_final = pd.concat([df_keep, combined], ignore_index=True)

    return df_final
