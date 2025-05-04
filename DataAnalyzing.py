import os
import numpy as np
import pandas as pd
input_path = r'C:\Users\97254\Downloads\DATA\meta_data.csv'
df = pd.read_csv(input_path)
subjects = [f"subject {i}" for i in range(12, 25)]
meetings = [1, 2, 3, 5, 6, 7, 9, 10, 11, 18]
states = ["baseline", "recovery", "therapy"]
for subject in subjects:
    subject_rows = []

    for meet in meetings:
        # Convert meet number to expected string (e.g., "meet1")
        meet_str = f"meet {meet}"

        # Extract Baseline
        baseline_value = df[
            (df["subject"] == subject) &
            (df["meet"] == meet_str) &
            (df["state"] == "baseline") &
            (df["col1"] == "  Mean HR (beats/min):        ")
            ]["col2"].values
        baseline_value = baseline_value[0] if len(baseline_value) > 0 else "NA"

        # Extract Recovery HR
        recovery_value = df[
            (df["subject"] == subject) &
            (df["meet"] == meet_str) &
            (df["state"] == "recovery") &
            (df["col1"] == "  Mean HR (beats/min):        ")
            ]["col2"].values
        recovery_value = recovery_value[0] if len(recovery_value) > 0 else "NA"

        # Extract Therapy HR
        therapy_values_df = df[
            (df["subject"] == subject) &
            (df["meet"] == meet_str) &
            (df["state"] == "therapy") &
            (df["col1"] == "  Mean HR (beats/min):        ")
            ]

        # Get the first 4 therapy values
        therapy_values = therapy_values_df["col2"].values[:4]

        # Fill missing values with NaN if less than 4
        while len(therapy_values) < 4:
            therapy_values = np.append(therapy_values, np.nan)

        # Calculate the average of the therapy values
        therapy_avg = np.nanmean(therapy_values)

        # Add to subject's data
        subject_rows.append([
            meet,
            baseline_value,
            recovery_value,
            therapy_values[0],
            therapy_values[1],
            therapy_values[2],
            therapy_values[3],
            therapy_avg
        ])

    # Create DataFrame for the subject
    columns = [
        "Meeting", "Baseline HR", "Recovery HR",
        "Therapy1 HR", "Therapy2 HR", "Therapy3 HR", "Therapy4 HR", "Therapy Avg"
    ]
    subject_df = pd.DataFrame(subject_rows, columns=columns)
    output_dir = os.path.dirname(os.path.abspath(input_path))
    output_path = os.path.join(output_dir, f"{subject}_HR_summary.csv")
    # Save to CSV
    subject_df.to_csv(output_path, index=False)