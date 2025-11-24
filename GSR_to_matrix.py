import os
import pandas as pd
import numpy as np

# Import your existing functions (or include them if standalone)
from GSR_to_tables import (
    timing_to_dataframe,
    GSR_to_dataframe,
    preprocess,
    SAMPLING_RATE
)


def extract_samples_by_jumps_of_n(label: str, df_timing, df_data, subjects, sample_step=10):
    """
    Extracts every Nth sample for a given label across all subjects. N is given as an input, the wanted label as well.
    """
    label_data = {}

    for subj_id in subjects:
        try:
            start_time = df_timing.loc[label, subj_id]
        except KeyError:
            print(f"Label '{label}' not found for subject {subj_id}")
            continue

        if pd.isna(start_time):
            continue

        try:
            start_time_float = float(start_time)
        except (ValueError, TypeError):
            continue

        start_sample = int(start_time_float * SAMPLING_RATE)

        # For trauma, find the end point
        if label == 'trauma':
            try:
                end_time = df_timing.loc['end of recording', subj_id]
                if pd.isna(end_time):
                    continue
                end_sample = int(float(end_time) * SAMPLING_RATE)
            except KeyError:
                continue
        else:
            # For standard conditions, extract a reasonable duration (e.g., 180 seconds = 1800 samples)
            end_sample = start_sample + 1800  # Adjust this as needed

        # Make sure we don't exceed data bounds
        end_sample = min(end_sample, len(df_data))

        if start_sample >= len(df_data):
            continue

        # Extract the data for this subject
        try:
            subject_data = df_data[subj_id].iloc[start_sample:end_sample]
        except KeyError:
            continue

        # Extract every Nth sample
        samples_at_intervals = []
        for i in range(0, len(subject_data), sample_step):
            samples_at_intervals.append(subject_data.iloc[i])

        label_data[f'Subject_{subj_id}'] = samples_at_intervals

    return label_data


def create_combined_excel(df_timing, df_data, output_file, sample_step=10):
    """
    Creates 1 Excel file with 4 sheets (one for each label).
    Each sheet has subjects as columns and samples (every 10th) as rows.
    """
    subjects = preprocess(df_timing, df_data)

    if not subjects:
        print("No subjects to process")
        return

    labels = ['neut1', 'stress', 'neut2', 'trauma']

    # Create Excel writer object
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for label in labels:
            print(f"\nProcessing label: {label}")
            label_data = extract_samples_by_jumps_of_n(label, df_timing, df_data, subjects, sample_step)

            if not label_data:
                print(f"No data found for label: {label}")
                continue

            # Create DataFrame
            df_label = pd.DataFrame.from_dict(label_data, orient='index').T

            # Add sample index (10, 20, 30, etc.)
            df_label.index = [(i + 1) * sample_step for i in range(len(df_label))]
            df_label.index.name = 'Sample'

            # Write to sheet
            df_label.to_excel(writer, sheet_name=label)
            print(f"Added sheet: {label}")
            print(f"Shape: {df_label.shape} (rows x columns)")

            # Print sample of the result
            print(f"\nSample of {label} data (first 5 rows, first 3 columns):")
            print(df_label.iloc[:5, :3])
            print()

    print(f"\nAll sheets saved to: {output_file}")


if __name__ == "__main__":
    file_path = "/Users/jasmineerell/Documents/Research/data/GSR_RawData.xlsx"
    sheet_to_load = "T1"
    sheet_time = "timing_1"
    output_dir = "/Users/jasmineerell/Documents/Research/data"
    output_file = os.path.join(output_dir, "GSR_matrix_per_event.xlsx")

    print("Loading data...")
    timing = timing_to_dataframe(file_path, sheet_time)
    data = GSR_to_dataframe(file_path, sheet_to_load)

    create_combined_excel(timing, data, output_file, sample_step=10)

    print("\nDone! Check the Excel file with 4 sheets.")