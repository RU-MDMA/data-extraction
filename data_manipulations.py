#!/usr/bin/env python3
import pandas as pd
import numpy as np

COMBINED_LABEL = "meet 1-3 median"   # ASCII label for Excel friendliness

def extract_meeting_num(s: pd.Series) -> pd.Series:
    return (
        s.astype(str)
         .str.extract(r"(\d+)", expand=False)
         .astype("Int64")            # nullable int (allows <NA>)
    )

def safe_mode(series: pd.Series):
    """Mode if available; else first non-null; else NaN."""
    m = series.mode(dropna=True)
    if not m.empty:
        return m.iat[0]
    nn = series.dropna()
    return nn.iat[0] if not nn.empty else np.nan

def median_per_sample_across_m123(input_csv: str, output_csv: str) -> None:
    df = pd.read_csv(input_csv)

    if "meeting" not in df.columns:
        raise KeyError("Expected a 'meeting' column.")
    if "sub" not in df.columns:
        raise KeyError("Expected a 'sub' column.")

    df = df.copy()
    df["meeting_num"] = extract_meeting_num(df["meeting"])

    # Sort key (time preferred; otherwise original order)
    time_col = next((c for c in ["Time (hh:mm:ss)", "time", "Time"] if c in df.columns), None)
    if time_col:
        df["_sort_key"] = pd.to_timedelta(df[time_col].astype(str), errors="coerce").dt.total_seconds()
    else:
        df["_sort_key"] = np.arange(len(df))

    # Use only meetings 1–3
    df_123 = df[df["meeting_num"].isin([1, 2, 3])].copy()
    if df_123.empty:
        raise ValueError("No rows found for meetings 1–3.")

    # Group per subject AND state (so state is preserved)
    group_axes = ["sub"]
    if "state" in df_123.columns:
        group_axes.append("state")

    # Sample index within (sub, state, meeting) ordered by time/_sort_key
    df_123 = df_123.sort_values(group_axes + ["meeting_num", "_sort_key"])
    df_123["sample_idx"] = df_123.groupby(group_axes + ["meeting_num"]).cumcount() + 1

    # Numeric columns to aggregate
    numeric_cols = df_123.select_dtypes(include="number").columns.tolist()
    for helper in ["meeting_num", "_sort_key"]:
        if helper in numeric_cols:
            numeric_cols.remove(helper)

    # Median across meetings 1–3 for each (sub, state, sample_idx)
    med_numeric = (
        df_123.groupby(group_axes + ["sample_idx"], as_index=False)[numeric_cols]
              .median()
    )

    # Non-numeric columns: keep representative value (mode/first) PER (sub, state, sample_idx)
    non_numeric_cols = [c for c in df_123.columns if c not in numeric_cols]
    for dropc in ["meeting_num", "_sort_key"]:
        if dropc in non_numeric_cols:
            non_numeric_cols.remove(dropc)

    rep_non_numeric = (
        df_123.groupby(group_axes + ["sample_idx"], as_index=False)[non_numeric_cols]
              .agg(safe_mode)
    )

    # Merge back
    combined = pd.merge(rep_non_numeric, med_numeric, on=group_axes + ["sample_idx"], how="left")

    # Set final meeting name; DO NOT touch state/therapy
    combined["meeting"] = COMBINED_LABEL

    # Reorder like original and drop sample_idx in the CSV
    original_cols = df.columns.tolist()
    for hc in ["meeting_num", "_sort_key"]:
        if hc in original_cols:
            original_cols.remove(hc)
    if "meeting" not in original_cols:
        original_cols.insert(1, "meeting")
    if "sample_idx" in original_cols:
        original_cols.remove("sample_idx")

    final_cols = [c for c in original_cols if c in combined.columns] + \
                 [c for c in combined.columns if c not in original_cols and c != "sample_idx"]
    combined = combined.reindex(columns=final_cols)

    # Save (utf-8-sig helps Excel)
    combined.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"✅ Wrote: {output_csv} | rows: {len(combined)}")

# ----- Run directly from PyCharm -----
if __name__ == "__main__":
    median_per_sample_across_m123(
        "/Users/jasmineerell/Documents/Research/block_test.csv",
        "/Users/jasmineerell/Documents/Research/block_test_per_sample_median.csv"
    )
