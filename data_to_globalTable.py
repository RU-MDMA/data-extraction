import pandas as pd
import re

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

def generate_global_metadata(meta_data_csv, output_csv):
    df = pd.read_csv(meta_data_csv, dtype=str).fillna("")

    # Filter only rows where col1 is a feature we care about
    df_filtered = df[df["col1"].isin(ALLOWED_FEATURES)].copy()

    if df_filtered.empty:
        print("No matching features found in meta_data.csv")
        return

    # Keep only the relevant columns
    df_filtered = df_filtered[["subject", "meet", "state", "type", "col1", "col2"]]

    # Encode therapy type into state (therapy_a, therapy_b...) to match original behavior
    def encode_state(row):
        if row["state"].lower() == "therapy" and row["type"]:
            return f"therapy_{row['type'].lower()}"
        return row["state"].lower()

    df_filtered["state"] = df_filtered.apply(encode_state, axis=1)
    df_filtered = df_filtered.drop(columns=["type"])
    df_filtered["type"] = "global"

    df_filtered = df_filtered.drop_duplicates()
    df_filtered = df_filtered.sort_values(by=["subject", "meet", "state"])

    df_filtered.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"Saved to {output_csv}")


if __name__ == "__main__":
    meta_data_csv = "/Users/jasmineerell/Documents/CS-second-year/MDMA/data-2026/meta_data.csv"
    output_csv = "/Users/jasmineerell/Documents/CS-second-year/MDMA/data-2026/global_metadata.csv"
    generate_global_metadata(meta_data_csv, output_csv)