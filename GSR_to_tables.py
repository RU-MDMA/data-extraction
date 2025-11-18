import os
import pandas as pd
import math 
import numpy as np
SAMPLING_RATE = 10
STANDARD_CONDITIONS = ['neut1', 'stress', 'neut2'] #act the same
TRAUMA_CONDITION = 'trauma'
#[duration,offset]
STANDARD_SEGMENTS = {
    'Baseline': [15,-15], 
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



def timing_to_dataframe(file_path: str, sheet_to_load:str):
    """
    Reads an timing excel file, replaces empty cells with 'NA', and changes first colums name to "event"
    returns Dataframe
    """
    df = pd.read_excel(file_path, sheet_name=sheet_to_load, index_col=0, na_values=['NA', ''])
    df.columns = df.columns.astype(str)
    #df = df.rename(columns={'Unnamed: 0': "event"})


    return df

def GSR_to_dataframe(file_path: str, sheet_to_load:str):
    """
    Reads an timing excel file, replaces empty cells with 'NA', and changes first colums name to "event"
    returns Dataframe
    """

    df = pd.read_excel(file_path, sheet_name=sheet_to_load, na_values=['NA', ''])
    df.columns = df.columns.astype(str)
    return df

def get_timing_by_id(df, id:int):
    return df[id]

def get_data_by_id(df, id:int):
    return df[id]

def avg_by_event_and_id(event:str, id, df_timing, df_data, seconds,offset_sec: int):
    """
    event: str, by the event we decide what specific time from the recording to take the samples 
    id: int, patient id
    df_timing, df_data: dataframes of the FULL data 
    second: int, time frame for the average computation
    offset_sec: int, relative starting point
    """
    id_str = str(id)

    try:
        start_time = df_timing.loc[event, id_str] # Gets the stating time from timing table
    except KeyError:
        return np.nan

    #if there is no starting time (missing data)    
    if pd.isna(start_time):
        return np.nan 
        
    start_time_sample = int(start_time * SAMPLING_RATE) #example - 660=66*10
    #SAMPLING_RATE is a global variable: how many samples per second
    start_time_sample = start_time_sample + int(offset_sec * SAMPLING_RATE) #example - -15*10 = -150 + 660 = 510 is the start sample
    num_of_rows_to_compute = int(seconds * SAMPLING_RATE)
    time_end_sample = start_time_sample + num_of_rows_to_compute

    if start_time_sample < 0 or time_end_sample > len(df_data):
        return np.nan
    try:
        sub_rows = df_data[id_str].iloc[start_time_sample:time_end_sample]
    except KeyError:
        return np.nan
    
    mean_val = sub_rows.mean() #computes average for second (over $seconds time)

    return mean_val

def create_statistic_table(df_timing, df_data):

    subjects = preprocess(df_timing,df_data)
    
    #building the table
    stats_cols = []
    for cond in STANDARD_CONDITIONS:
        for seg in STANDARD_SEGMENTS.keys():
            stats_cols.append(f'{cond}_{seg}_Mean')
    
    trauma_base_segments = ['Baseline', 'Audio', 'Imagery']
    for seg in trauma_base_segments:
        stats_cols.append(f'{TRAUMA_CONDITION}_{seg}_Mean')
    for i in range(1, 10): 
        stats_cols.append(f'{TRAUMA_CONDITION}_Recovery_{i}_Mean')


    df_stats = pd.DataFrame(index=subjects, columns=stats_cols, dtype=float)
    df_stats.index.name = 'Subject_ID' 

    # filling the table
    for subj_id in subjects:
        for condition in STANDARD_CONDITIONS: #all except traume
            for seg_name, (duration, offset) in STANDARD_SEGMENTS.items():
                
                #computing the avg and placing in the table
                mean_result = avg_by_event_and_id(
                    event=condition, 
                    id=subj_id, 
                    df_timing=df_timing, 
                    df_data=df_data, 
                    seconds=duration, 
                    offset_sec=offset
                )
                
                col_name = f'{condition}_{seg_name}_Mean'
                df_stats.loc[subj_id, col_name] = mean_result
        
        #Trauma
        condition = TRAUMA_CONDITION
        
        try:
            trauma_onset_sec = df_timing.loc[condition, subj_id]
            trauma_audio_end_sec = df_timing.loc[TRAUMA_AUDIO_END_LABEL, subj_id]
            recording_end_sec = df_timing.loc[RECORDING_END_LABEL, subj_id]

        except KeyError:
            print(f"missing Trauma End/Recording End for subject {subj_id}")
            continue #skip i case of missing information

        is_time_missing = pd.isna(trauma_onset_sec) or pd.isna(trauma_audio_end_sec) or pd.isna(recording_end_sec)        
        if is_time_missing:
            continue 
        
        #baseline for trauma is the same
        baseline_mean = avg_by_event_and_id(condition, subj_id, df_timing, df_data, BASELINE_DURATION, BASELINE_OFFSET)
        df_stats.loc[subj_id, f'{condition}_Baseline_Mean'] = baseline_mean
        
        #audio
        audio_duration_sec = trauma_audio_end_sec - trauma_onset_sec
        audio_mean = avg_by_event_and_id(condition, subj_id, df_timing, df_data, audio_duration_sec, AUDIO_OFFSET)
        df_stats.loc[subj_id, f'{condition}_Audio_Mean'] = audio_mean

        #imagery
        imagery_offset_sec = audio_duration_sec
        duration = STANDARD_SEGMENTS["Imagery"][0]
        imagery_mean = avg_by_event_and_id(condition, subj_id, df_timing, df_data, duration, imagery_offset_sec)
        df_stats.loc[subj_id, f'{condition}_Imagery_Mean'] = imagery_mean
        
        #recovery
        recovery_start_offset_sec = imagery_offset_sec + IMAGERY_DURATION 
        recovery_start_sec = trauma_onset_sec + recovery_start_offset_sec
        total_recovery_duration = recording_end_sec - recovery_start_sec
        
        # how many recovery blocks exist
        num_recovery_blocks = math.floor(total_recovery_duration / RECOVERY_BLOCK_DURATION)
        print(num_recovery_blocks)
        
        current_offset = recovery_start_sec
        
        for i in range(1, num_recovery_blocks + 1):
            recovery_mean = avg_by_event_and_id(
                condition, subj_id, df_timing, df_data, 
                RECOVERY_BLOCK_DURATION, 
                current_offset
            )
            df_stats.loc[subj_id, f'{condition}_Recovery_{i}_Mean'] = recovery_mean
            current_offset += RECOVERY_BLOCK_DURATION
            
    return df_stats

def preprocess(df_timing,df_data):
    """
    takes as an input timing dataframe and data dataframe and returns common subjects id list. 
    if some is missing it alerts and "ignores" the missing data
    """
    timing_subjects = set(df_timing.columns.astype(str).tolist())
    data_subjects = set(df_data.columns.astype(str).tolist())
    
    subjects = list(timing_subjects.intersection(data_subjects))
    
    if not subjects:
        print("no common subjects ids in the data")
        return pd.DataFrame()
    return subjects

def dataframe_to_csv(df):
    output_file_name_csv = 'GSR_Statistics_Table.csv'

    df.to_csv(
        output_file_name_csv, 
        index=True,        
        float_format='%.8f' 
    )


if __name__ == "__main__":
    file_path = "../GSR_RawData.xlsx"
    sheet_to_load = "T1"
    sheet_time = "timing_1"
    timing = timing_to_dataframe(file_path,sheet_time)
    data = GSR_to_dataframe(file_path,sheet_to_load)

    #mean = avg_by_event_and_id("neut1",18,timing,data,30)
    #print("{:.10f}".format(mean))

    stat = create_statistic_table(timing,data)
    dataframe_to_csv(stat)





