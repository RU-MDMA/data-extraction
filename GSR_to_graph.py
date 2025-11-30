import os
import pandas as pd
import math 
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

SAMPLING_RATE = 10
STARTING_OFFSET = 10
STANDARD_CONDITIONS = ['neut1', 'stress', 'neut2']
TRAUMA_CONDITION = 'trauma'
STANDARD_SEGMENTS = {
    'Baseline': [10,-STARTING_OFFSET], 
    'Audio': [60,0],   
    'Imagery': [30,60],  
    'Recovery_1': [30,90],
    'Recovery_2': [30,120],
}
TRAUMA_AUDIO_END_LABEL = 'trauma_end'  
RECORDING_END_LABEL = 'end of recording' 
RECOVERY_BLOCK_DURATION = 30 
BASELINE_DURATION = STANDARD_SEGMENTS['Baseline'][0]
BASELINE_OFFSET = STANDARD_SEGMENTS['Baseline'][1]
IMAGERY_DURATION = STANDARD_SEGMENTS['Imagery'][0]
AUDIO_OFFSET = STANDARD_SEGMENTS['Audio'][1]
COLORS = {'neut1': 'lightblue', 'stress': 'purple', 'neut2': 'blue', 'trauma': 'red'}
PLOT_SEGMENT_DURATION_SEC = 210 
PLOT_SEGMENT_SAMPLES = int(PLOT_SEGMENT_DURATION_SEC * SAMPLING_RATE)
OUTPUT_DIR = '/Users/yuvalnadam/Desktop/CS/Cognition/MDMA/2ndYear/data/GSR/Diagnostic_Figures_Output'
# ----------------------------------------------------------------------

def timing_to_dataframe(file_path: str, sheet_to_load:str):
    df = pd.read_excel(file_path, sheet_name=sheet_to_load, index_col=0, na_values=['NA', ''])
    df.columns = df.columns.astype(str)
    return df

def GSR_to_dataframe(file_path: str, sheet_to_load:str):
    df = pd.read_excel(file_path, sheet_name=sheet_to_load, na_values=['NA', ''])
    df.columns = df.columns.astype(str)
    return df


# Subplot 1
def prepare_raw_data_for_plot(subj_id, df_timing, df_data):

    id_str = str(subj_id)
    
    try:

        neut1_onset_sec = df_timing.loc['neut1', id_str]
        plot_start_sec = neut1_onset_sec - STARTING_OFFSET 
        
        plot_end_sec = df_timing.loc[RECORDING_END_LABEL, id_str]
        
    except Exception as e:
        print(f"missing timing {subj_id}. {e}")
        return None, None
    
    plot_start_sample = int(plot_start_sec * SAMPLING_RATE)
    plot_end_sample = int(plot_end_sec * SAMPLING_RATE)
    
    try:
        raw_gsr_series = df_data[id_str].iloc[plot_start_sample : plot_end_sample]
    except Exception as e:
        print(f"for {subj_id}. samples missing {plot_start_sample}:{plot_end_sample}. {e}")
        return None, None
        
    return raw_gsr_series, plot_start_sec

def plot_raw_data_and_events(gsr_series, subj_id, df_timing, plot_start_sec):
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    time_axis = np.arange(0, len(gsr_series) / SAMPLING_RATE, 1 / SAMPLING_RATE)
    if len(time_axis) > len(gsr_series):
        time_axis = time_axis[:len(gsr_series)]

    ax.plot(time_axis, gsr_series.values, color='gray', alpha=0.7, label='Raw GSR')
    ax.set_title(f'Raw GSR Signal and Events (Subject {subj_id})')
    ax.set_xlabel(f'Time Relative to Start of Plot ({plot_start_sec:.2f}s) [Seconds]')
    ax.set_ylabel('Raw GSR Amplitude')
    ax.grid(axis='y', linestyle='--')
    
    for event in ['neut1', 'stress', 'neut2', 'trauma']:
        try:
            onset_sec = df_timing.loc[event, str(subj_id)]
            
            onset_relative_time = onset_sec - plot_start_sec
            
            # (Imagery Onset)
            if event == 'trauma':
                end_audio_sec = df_timing.loc[TRAUMA_AUDIO_END_LABEL, str(subj_id)]
            else:
                end_audio_sec = onset_sec + STANDARD_SEGMENTS["Audio"][0] 

            end_audio_relative_time = end_audio_sec - plot_start_sec
            
            # Audio Onset Marker
            ax.axvline(x=onset_relative_time, color=COLORS[event], linestyle='-', linewidth=1.5, label=f'{event} Audio Onset')
            
            # Imagery Onset Marker
            ax.axvline(x=end_audio_relative_time, color=COLORS[event], linestyle='--', linewidth=1.5)
            
        except Exception:
            continue
    
    ax.legend()
    plt.tight_layout()
    output_filename = f'Subplot_1_Test_Subj_{subj_id}.png'
    plt.savefig(output_filename)
    print(f"\n subplot1 : {output_filename}")

def get_baseline_mean(event, id_str, df_timing, df_data):
    
    try:
        start_time = df_timing.loc[event, id_str]
    except KeyError:
        return np.nan
    
    if pd.isna(start_time): return np.nan 
    try:
        start_time_float = float(start_time)
    except (ValueError, TypeError): 
        return np.nan
        
    onset_sample_abs = int(start_time_float * SAMPLING_RATE) 
    baseline_start_sample = onset_sample_abs + int(BASELINE_OFFSET * SAMPLING_RATE)
    baseline_end_sample = baseline_start_sample + int(BASELINE_DURATION * SAMPLING_RATE)

    if baseline_start_sample < 0 or baseline_end_sample > len(df_data):
        return np.nan
        
    try:
        baseline_series = df_data[id_str].iloc[baseline_start_sample:baseline_end_sample]
    except KeyError:
        return np.nan

    return baseline_series.mean()

def create_diagnostic_figures(subj_id, df_timing, df_data, data_sheet_name):    
    id_str = str(subj_id)
    #creating two figures - subplot1,subplot2

    fig, axes = plt.subplots(2, 1, figsize=(15, 8), sharex=False)
    
    # --- Subplot 1: Raw GSR Signal ---
    
    try:
        neut1_onset_sec = df_timing.loc['neut1', id_str]
        plot_start_sec = neut1_onset_sec - STARTING_OFFSET 
        plot_end_sec = df_timing.loc[RECORDING_END_LABEL, id_str]
        
        plot_start_sample = int(plot_start_sec * SAMPLING_RATE)
        plot_end_sample = int(plot_end_sec * SAMPLING_RATE)
        
        raw_gsr_series = df_data[id_str].iloc[plot_start_sample : plot_end_sample]
        
        time_axis = np.arange(0, len(raw_gsr_series) / SAMPLING_RATE, 1 / SAMPLING_RATE)
        if len(time_axis) > len(raw_gsr_series): time_axis = time_axis[:len(raw_gsr_series)]

        axes[0].plot(time_axis, raw_gsr_series.values, color='gray', alpha=0.7)
        axes[0].set_title(f'Raw GSR Signal and Events (Subject {id_str})')
        axes[0].set_ylabel('Raw GSR Amplitude')

        # 2. adding markers (Audio ---- , Imagery: - - - )
        for event in ['neut1', 'stress', 'neut2', 'trauma']:
            try:
                onset_sec = df_timing.loc[event, id_str]
                if event == 'trauma':
                    end_audio_sec = df_timing.loc[TRAUMA_AUDIO_END_LABEL, id_str]
                else:
                    end_audio_sec = onset_sec + STANDARD_SEGMENTS['Audio'][0]

                onset_relative_time = onset_sec - plot_start_sec
                end_audio_relative_time = end_audio_sec - plot_start_sec
                
                axes[0].axvline(x=onset_relative_time, color=COLORS[event], linestyle='-', linewidth=1.5, label=f'{event} Audio Onset')
                axes[0].axvline(x=end_audio_relative_time, color=COLORS[event], linestyle='--', linewidth=1.5)
            except Exception:
                continue
        axes[0].legend()
        axes[0].grid(axis='y', linestyle='--')
        
    except Exception as e:
        axes[0].set_title(f'Raw Data Missing/Error for Subject {id_str}')
        print(f"Error Subplot 1: {e}")
        
    # ----------------------------------------------------
    # Subplot 2: Baseline-Normalised Segments
    # ----------------------------------------------------
    
    normalized_segments = {}
    for event in ['neut1', 'stress', 'neut2', 'trauma']:
        try:
            baseline_mean = get_baseline_mean(event, id_str, df_timing, df_data)
            
            if pd.isna(baseline_mean) or baseline_mean <= 0:
                print(f"negative or missing baseline {event}")
                continue

            # extract the full segment
            onset_sec = df_timing.loc[event, id_str]
            segment_start_sec = onset_sec - STARTING_OFFSET
            
            segment_start_sample = int(segment_start_sec * SAMPLING_RATE)
            segment_end_sample = segment_start_sample + PLOT_SEGMENT_SAMPLES
            
            if segment_end_sample > len(df_data) or segment_start_sample < 0: continue

            segment_series = df_data[id_str].iloc[segment_start_sample : segment_end_sample]
            normalized_series = segment_series / baseline_mean
            normalized_segments[event] = normalized_series
            
        except Exception:
            continue

    # plotting all
    for event, series in normalized_segments.items():
        time_axis_relative = np.linspace(-STARTING_OFFSET, PLOT_SEGMENT_DURATION_SEC - STARTING_OFFSET, len(series))
        
        axes[1].plot(time_axis_relative, series.values, color=COLORS[event], label=event)
        
        # Audio End Marker
        if event == 'trauma':
            end_audio_sec = df_timing.loc[TRAUMA_AUDIO_END_LABEL, id_str]
            audio_duration = end_audio_sec - df_timing.loc[event, id_str]
        else:
            audio_duration = STANDARD_SEGMENTS['Audio'][0]
        
        axes[1].axvline(x=audio_duration, color=COLORS[event], linestyle='--', alpha=0.7)

    axes[1].set_title('Baseline-Normalised Segments (Aligned to Audio Onset)')
    axes[1].set_xlabel('Time Relative to Audio Onset (Seconds)')
    axes[1].set_ylabel('GSR Amplitude (Normalised: 1.0 = Baseline)')
    axes[1].axvline(x=0, color='black', linestyle='-', alpha=0.7)
    axes[1].axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
    axes[1].legend()
    axes[1].grid(axis='y', linestyle='--')
    
    # output dir
    os.makedirs(OUTPUT_DIR, exist_ok=True) 
    

    output_filename = os.path.join(OUTPUT_DIR, f'Diagnostic_Figure_Subj_{id_str}_{data_sheet_name}.png')    
    plt.savefig(output_filename)
    print(f"\n (2 Subplots) {output_filename}")
    plt.close(fig) 

def preprocess(df_timing,df_data):
    """
    takes as an input timing dataframe and data dataframe and returns common subjects id list. 
    if some is missing it alerts and "ignores" the missing data
    """
    timing_columns_ordered = df_timing.columns.astype(str).tolist()
    timing_subjects_set = set(timing_columns_ordered)
    data_subjects_set = set(df_data.columns.astype(str).tolist())
    
    missing_in_data = timing_subjects_set - data_subjects_set
    missing_in_timing = data_subjects_set - timing_subjects_set
    
    if missing_in_data:
        print(f"subjects with time table and no data(df_data): {sorted(list(missing_in_data))}")
    
    if missing_in_timing:
        print(f"some subject are missing time table(df_timing): {sorted(list(missing_in_timing))}")
    
    subjects = [subj for subj in timing_columns_ordered if subj in data_subjects_set]
    
    if not subjects:
        print("no common subjects ids in the data")
        return pd.DataFrame()
    return subjects

def process_all_diagnostic_figures(file_path, data_sheet_names):


    for sheet_name in data_sheet_names:
        
        # 1. קביעת שם גיליון הזמנים (בהנחה ש-T1 משתמש ב-timing_1, T2 ב-timing_2 וכו')
        # sheet_name[-1] מושך את '1' מתוך 'T1'
        timing_sheet_name = f'timing_{sheet_name[-1]}' 

        try:
            timing = timing_to_dataframe(file_path, timing_sheet_name)
            data = GSR_to_dataframe(file_path, sheet_name)
            
            subjects_to_process = preprocess(timing, data) 
            
            for subj_id in subjects_to_process:
                print(f"--- plotting for subject: {subj_id} ---")
                create_diagnostic_figures(subj_id, timing, data, sheet_name)

        except Exception as e:
            print(f"\n error while working on sheet {sheet_name}: {e}")
            continue

    

if __name__ == "__main__":
    FILE_PATH = '/Users/yuvalnadam/Desktop/CS/Cognition/MDMA/2ndYear/data/GSR/GSR_RawData.xlsx' 
    SHEET_DATA = 'T1'
    SHEET_TIMING = 'timing_1'
    #SUBJECT_ID_TO_PLOT = 18
    DATA_SHEET_NAMES = ['T1', 'T2']

    timing = timing_to_dataframe(FILE_PATH, SHEET_TIMING)
    data = GSR_to_dataframe(FILE_PATH, SHEET_DATA)

    process_all_diagnostic_figures(FILE_PATH, DATA_SHEET_NAMES)

    """
    gsr_series, plot_start_sec = prepare_raw_data_for_plot(SUBJECT_ID_TO_PLOT, timing, data)
    create_diagnostic_figures(SUBJECT_ID_TO_PLOT, timing, data)

    if gsr_series is not None:
        plot_raw_data_and_events(gsr_series, SUBJECT_ID_TO_PLOT, timing, plot_start_sec)
    else:
        print("could not load data")"""