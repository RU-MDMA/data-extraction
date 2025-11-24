import os
import pandas as pd
import numpy as np

# Import your existing functions
from GSR_to_tables import (
    timing_to_dataframe,
    GSR_to_dataframe,
    preprocess,
    SAMPLING_RATE,
)


def extract_samples_for_label(label: str, df_timing, df_data, subjects, sample_step=10):
    """
    Extracts every Nth sample for a given label across all subjects.
    The timing table contains END times for each label.

    - neut1: from 0 to neut1_time
    - stress: from neut1_time to stress_time
    - neut2: from stress_time to neut2_time
    - trauma: from neut2_time to 'end of recording' (or trauma_end if used)
    """
    label_data = {}

    # Define the previous label for each condition (to get start time)
    previous_label = {
        "neut1": None,  # starts at 0
        "stress": "neut1",
        "neut2": "stress",
        "trauma": "neut2",
    }

    prev_label = previous_label.get(label)
    if prev_label is None and label != "neut1":
        print(f"Unknown label: {label}")
        return label_data

    for subj_id in subjects:
        # Make sure the subject exists in data
        if subj_id not in df_data.columns:
            print(f"Subject {subj_id} not found in data, skipping.")
            continue

        # --- 1. Get END time from timing table ---

        try:
            end_time = df_timing.loc[label, subj_id]
        except KeyError:
            print(f"Label '{label}' not found for subject {subj_id}")
            continue

        if pd.isna(end_time):
            print(f"End time NaN for label '{label}', subject {subj_id}")
            continue

        try:
            end_time_float = float(end_time)
        except (ValueError, TypeError):
            print(f"End time non-numeric for label '{label}', subject {subj_id}: {end_time}")
            continue

        # For trauma, we prefer 'end of recording' (or trauma_end) as the true end
        if label == "trauma":
            # Try 'end of recording' first, then 'trauma_end' as fallback
            for row_name in ["end of recording", "trauma_end"]:
                if row_name in df_timing.index:
                    val = df_timing.loc[row_name, subj_id]
                    if not pd.isna(val):
                        try:
                            end_time_float = float(val)
                            break
                        except (ValueError, TypeError):
                            pass

        # --- 2. Get START time (0 or previous label end) ---

        if label == "neut1":
            start_time_float = 0.0
        else:
            try:
                start_time = df_timing.loc[prev_label, subj_id]
            except KeyError:
                print(f"Previous label '{prev_label}' not found for subject {subj_id}")
                continue

            if pd.isna(start_time):
                print(f"Start time NaN for '{prev_label}', subject {subj_id}")
                continue

            try:
                start_time_float = float(start_time)
            except (ValueError, TypeError):
                print(f"Start time non-numeric for '{prev_label}', subject {subj_id}: {start_time}")
                continue

        # --- 3. Convert times to sample indices ---

        start_sample = int(start_time_float * SAMPLING_RATE)
        end_sample = int(end_time_float * SAMPLING_RATE)

        if end_sample <= start_sample:
            print(
                f"Invalid sample range for subject {subj_id}, label {label}: "
                f"{start_sample}–{end_sample}"
            )
            continue

        # --- 4. Slice the subject's column STRICTLY by timing ---

        col = df_data[subj_id].reset_index(drop=True)
        n_available = len(col)

        # We do NOT want to go past the timing, but we also must
        # not go beyond the available data.
        if start_sample >= n_available:
            print(
                f"Start sample {start_sample} beyond available data ({n_available}) "
                f"for subject {subj_id}, label {label}"
            )
            continue

        # Clamp end_sample to available data, but never extend past timing-derived end_sample
        end_sample_clamped = min(end_sample, n_available)

        subject_data = col.iloc[start_sample:end_sample_clamped]

        # Expected length from timing (in samples)
        expected_len = end_sample - start_sample

        # Optional strict truncation (shouldn't usually be needed,
        # but it guarantees we never pass the timing end).
        if len(subject_data) > expected_len:
            subject_data = subject_data.iloc[:expected_len]

        # Debug for subject 18 trauma
        if str(subj_id) == "18" and label == "trauma":
            print("\n*** DEBUG SUBJECT 18 – TRAUMA ***")
            print(f"Timing start: {start_time_float} sec")
            print(f"Timing end:   {end_time_float} sec")
            print(f"start_sample: {start_sample}")
            print(f"end_sample:   {end_sample}")
            print(f"len(col):     {n_available}")
            print(f"len(subject_data): {len(subject_data)}")
            print(f"expected_len (samples): {expected_len}")
            print("*** END DEBUG ***\n")

        # --- 5. Extract every Nth sample ---

        samples_at_intervals = []
        for i in range(0, len(subject_data), sample_step):
            samples_at_intervals.append(subject_data.iloc[i])

        # Save
        label_data[f"Subject_{subj_id}"] = samples_at_intervals

        # Debug info
        duration_sec = end_time_float - start_time_float
        print(
            f"  Subject {subj_id}: {start_time_float:.1f}-{end_time_float:.1f} sec "
            f"= {duration_sec:.1f} sec ({len(subject_data)} samples) "
            f"-> {len(samples_at_intervals)} extracted"
        )

    return label_data


def create_combined_excel(df_timing, df_data, timepoint, sample_step=10):
    """
    Creates sheets for a given timepoint (T1 or T2).
    Each sheet has subjects as columns and samples (every Nth) as rows.
    """
    subjects = preprocess(df_timing, df_data)

    if not subjects:
        print(f"No subjects to process for {timepoint}")
        return None

    labels = ["neut1", "stress", "neut2", "trauma"]
    sheets_data = {}

    for label in labels:
        print(f"\nProcessing {timepoint} - label: {label}")
        label_data = extract_samples_for_label(label, df_timing, df_data, subjects, sample_step)

        if not label_data:
            print(f"No data found for {timepoint} - label: {label}")
            continue

        # Create DataFrame: rows = samples (every Nth), columns = subjects
        df_label = pd.DataFrame.from_dict(label_data, orient="index").T

        # Add sample index (10, 20, 30, etc.)
        df_label.index = [(i + 1) * sample_step for i in range(len(df_label))]
        df_label.index.name = "Sample"

        # Store with timepoint suffix
        sheet_name = f"{label} {timepoint}"
        sheets_data[sheet_name] = df_label

        print(f"Prepared sheet: {sheet_name}")
        print(f"Shape: {df_label.shape} (rows x columns)")

        # Print sample of the result
        print(f"\nSample of {sheet_name} data (first 5 rows, first 3 columns):")
        print(df_label.iloc[:5, :3])
        print()

    return sheets_data


if __name__ == "__main__":
    file_path = "/Users/jasmineerell/Documents/Research/data/GSR_RawData.xlsx"
    output_dir = "/Users/jasmineerell/Documents/Research/data"
    output_file = os.path.join(output_dir, "GSR_matrix_per_event.xlsx")

    # Define timepoints and their corresponding sheets
    timepoints = {
        "T1": {"data_sheet": "T1", "timing_sheet": "timing_1"},
        "T2": {"data_sheet": "T2", "timing_sheet": "timing_2"},
    }

    all_sheets = {}

    # Process each timepoint
    for timepoint, sheets in timepoints.items():
        print(f"\n{'=' * 60}")
        print(f"Processing {timepoint}")
        print(f"{'=' * 60}")

        print(
            f"Loading data from sheets: {sheets['data_sheet']} and {sheets['timing_sheet']}..."
        )

        timing = timing_to_dataframe(file_path, sheets["timing_sheet"])
        data = GSR_to_dataframe(file_path, sheets["data_sheet"])

        # Create sheets for this timepoint
        timepoint_sheets = create_combined_excel(timing, data, timepoint, sample_step=10)

        if timepoint_sheets:
            all_sheets.update(timepoint_sheets)

    # Write all sheets to one Excel file
    if all_sheets:
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            for sheet_name, df in all_sheets.items():
                df.to_excel(writer, sheet_name=sheet_name)
                print(f"Added sheet: {sheet_name}")
    else:
        print("\nNo data to write!")

    print("\nDone! Check the Excel file with all T1 and T2 sheets.")
