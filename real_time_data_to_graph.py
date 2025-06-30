import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

"""# === Configurable Variables ===
EXCEL_PATH = 'data.xlsx'            # Path to your Excel file
SUBJECT_ID = 15                     # Subject ID to plot
OUTPUT_DIR = '.'                    # Directory to save the output
PARAMETER_NAME = 'Mean HR'          # Change to any parameter name from the Excel"""

# === Load and clean data ===
def load_clean_data(filepath, parameter_name):
    print(filepath)
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip()

    # Find the actual parameter column
    param_col = [col for col in df.columns if parameter_name in col][0]
    print("Using parameter column:", param_col)

    # Find the actual time column
    time_col = [col for col in df.columns if 'Time' in col and 'hh' in col][0]
    print("Using time column:", time_col)

    df = df[pd.to_numeric(df['sub'], errors='coerce').notnull()].copy()
    df['sub'] = df['sub'].astype(int)
    df['meeting'] = df['meeting'].astype(int)
    df[param_col] = pd.to_numeric(df[param_col], errors='coerce')
    df.rename(columns={param_col: 'value', time_col: 'Time'}, inplace=True)

    df['state'] = df['state'].str.strip().str.lower()
    df['therapy'] = df['therapy'].astype(str).str.strip().str.upper()
    df['Time'] = df['Time'].astype(str).str.strip()
    return df

#VERSION 2 - SHOWS EMPTY SPACE FOR NAN DATA
def plot_subject_meetings(df, subject_id, parameter_name, output_dir):
    subject_data = df[df['sub'] == subject_id]
    meetings = sorted(subject_data['meeting'].unique())

    fig, axs = plt.subplots(4, 3, figsize=(18, 12))
    axs = axs.flatten()

    for idx, meeting in enumerate(meetings):
        ax = axs[idx]
        meet_data = subject_data[subject_data['meeting'] == meeting]
        bars, colors, xtick_labels = [], [], []

        # === Baseline ===
        baseline = meet_data[(meet_data['state'] == 'baseline')]
        if len(baseline) > 0:
            values = baseline['value'].dropna()
            bars += list(values)
            colors += ['blue'] * len(values)
            xtick_labels += list(baseline['Time'].fillna('').astype(str).str[-5:])
            num_missing = len(baseline) - len(values)
            bars += [0] * num_missing
            colors += ['lightgray'] * num_missing
            xtick_labels += [''] * num_missing
        else:
            bars += [0]
            colors += ['lightgray']
            xtick_labels += ['']

        # === Therapy A–D ===
        for stage in ['A', 'B', 'C', 'D']:
            therapy_all = meet_data[(meet_data['state'] == 'therapy') & (meet_data['therapy'] == stage)]
            if len(therapy_all) > 0:
                values = therapy_all['value'].dropna()
                bars += list(values)
                colors += ['pink'] * len(values)
                xtick_labels += list(therapy_all['Time'].fillna('').astype(str).str[-5:])
                num_missing = len(therapy_all) - len(values)
                bars += [0] * num_missing
                colors += ['lightgray'] * num_missing
                xtick_labels += [''] * num_missing
            else:
                bars += [0]
                colors += ['lightgray']
                xtick_labels += ['']

        # === Recovery ===
        recovery = meet_data[(meet_data['state'] == 'recovery')]
        if len(recovery) > 0:
            values = recovery['value'].dropna()
            bars += list(values)
            colors += ['green'] * len(values)
            xtick_labels += list(recovery['Time'].fillna('').astype(str).str[-5:])
            num_missing = len(recovery) - len(values)
            bars += [0] * num_missing
            colors += ['lightgray'] * num_missing
            xtick_labels += [''] * num_missing
        else:
            bars += [0]
            colors += ['lightgray']
            xtick_labels += ['']

        # === Draw the bars ===
        bar_container = ax.bar(range(len(bars)), bars, color=colors)
        ax.set_title(f"Meet {meeting}", fontsize=12)
        ax.set_xlabel("Time (HH:MM)", fontsize=10)
        ax.set_ylabel(parameter_name, fontsize=10)

        # X-axis label handling
        if len(xtick_labels) > 20:
            visible_ticks = list(range(0, len(xtick_labels), 5))
            ax.set_xticks(visible_ticks)
            ax.set_xticklabels([xtick_labels[i] for i in visible_ticks], rotation=45, ha='right', fontsize=6)
        else:
            ax.set_xticks(range(len(xtick_labels)))
            ax.set_xticklabels(xtick_labels, rotation=45, ha='right', fontsize=6)

    # Remove unused subplots
    for j in range(len(meetings), len(axs)):
        fig.delaxes(axs[j])

    # Legend
    fig.legend(handles=[
        mpatches.Patch(color='blue', label='Baseline'),
        mpatches.Patch(color='pink', label='Therapy'),
        mpatches.Patch(color='green', label='Recovery'),
        mpatches.Patch(color='lightgray', label='Missing Data')
    ], loc='lower right', fontsize=10)

    plt.tight_layout()
    filename = f"subject_{subject_id}_{parameter_name.replace(' ', '_').lower()}_analysis.png"
    plt.savefig(os.path.join(output_dir, filename), dpi=300)
    plt.close()
    print(f"✅ Saved: {filename}")

# === Run the script ===
def generate_graphs(excel_path, parameter, subject_id, output_dir):
    df = load_clean_data(excel_path, parameter)
    os.makedirs(output_dir, exist_ok=True)
    plot_subject_meetings(df, subject_id, parameter, output_dir)

def generate_graphs_for_all_subjects(excel_path, parameter, output_dir="."):
    """
    Detects all unique subjects in the Excel file and generates a graph for each.
    """
    print(f"Loading data from: {excel_path}")
    df = load_clean_data(excel_path, parameter)
    subject_ids = df['sub'].dropna().astype(int).unique()
    os.makedirs(output_dir, exist_ok=True)

    print(f"Found {len(subject_ids)} subjects: {list(subject_ids)}")
    for sid in subject_ids:
        print(f"   • Generating graph for subject {sid}...")
        try:
            plot_subject_meetings(df, sid, parameter, output_dir)
        except Exception as e:
            print(f"     Error for subject {sid}: {e}")

    print("All subject graphs generated.")


