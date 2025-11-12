#!/usr/bin/env python3
import pandas as pd


def extract_meeting_num_list(series: pd.Series) -> pd.Series:
    """Extract numeric meeting index (e.g. 'meet 1' → 1)"""
    return (
        series.astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype("Int64")
    )


def export_meetings_1_2_3_to_df(input_csv: str, output_csv: str) -> None:
    df = pd.read_csv(input_csv)

    # Validate column
    if "meeting" not in df.columns:
        raise KeyError("Expected a 'meeting' column in the CSV.")

    # Extract meeting numbers
    df["meeting_num"] = extract_meeting_num_list(df["meeting"])

    print("\n=== Counts BEFORE filtering ===")
    before = (
        df[df["meeting_num"].isin([1, 2, 3])]
        .groupby(["sub", "meeting_num"])
        .size()
        .unstack(fill_value=0)
    )
    print(before)

    # Filter meetings 1, 2, 3
    df_123 = df[df["meeting_num"].isin([1, 2, 3])].copy()

    print("\n=== Counts AFTER filtering (should be identical) ===")
    after = (
        df_123.groupby(["sub", "meeting_num"])
        .size()
        .unstack(fill_value=0)
    )
    print(after)

    # Sort nicely and export
    sort_cols = [c for c in ["sub", "state", "meeting_num", "meeting", "therapy"] if c in df_123.columns]
    if sort_cols:
        df_123 = df_123.sort_values(sort_cols)

    df_123.drop(columns=["meeting_num"], inplace=True)
    df_123.to_csv(output_csv, index=False)
    print(f"\n✅ Wrote: {output_csv}")
    print(f"Total rows exported: {len(df_123)}")


if __name__ == "__main__":
    export_meetings_1_2_3_to_df(
        "/Users/jasmineerell/Documents/Research/block_test.csv",
        "/Users/jasmineerell/Documents/Research/meetings_1_2_3_by_sub_state.csv"
    )
