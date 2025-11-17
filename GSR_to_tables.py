import os
import pandas as pd
SAMPLING_RATE = 10
CONDITIONS = ['neut1', 'stress', 'neut2', 'trauma']
SUB_SEGMENTS = {
    'Baseline': [-15,0], 
    'Audio': [0,60],   
    'Imagery': [60,90],  
    'Recovery_1': [90,120],
    'Recovery_2': [120,150],
}



def timing_to_dataframe(file_path: str, sheet_to_load:str):
    """
    Reads an timing excel file, replaces empty cells with 'NA', and changes first colums name to "event"
    returns Dataframe
    """
    df = pd.read_excel(file_path, sheet_name=sheet_to_load, index_col=0, na_values=['NA', ''])
    df = df.rename(columns={'Unnamed: 0': "event"})


    return df

def GSR_to_dataframe(file_path: str, sheet_to_load:str):
    """
    Reads an timing excel file, replaces empty cells with 'NA', and changes first colums name to "event"
    returns Dataframe
    """

    df = pd.read_excel(file_path, sheet_name=sheet_to_load, na_values=['NA', ''])
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
    time_start = int(df_timing.loc[event, id]) * SAMPLING_RATE #SAMPLING_RATE is a global variable: how many samples per second
    time_start_sample = time_start + (offset_sec * SAMPLING_RATE)
    num_of_rows_to_compute = seconds * SAMPLING_RATE
    time_end_sample = time_start_sample + num_of_rows_to_compute

    if time_start_sample < 0 or time_end_sample > len(df_data):
        return None
    
    sub_rows = df_data[id].iloc[time_start_sample:time_end_sample]
    mean_val = sub_rows.mean() #computes average for second (over $seconds time)

    return mean_val

def create_statistic_table(df_timing, df_data):
    
    subjects = df_timing.columns.astype(str).tolist() 
    
    stats_cols = []
    for cond in CONDITIONS:
        for seg in SUB_SEGMENTS.keys():
            stats_cols.append(f'{cond}_{seg}_Mean')

    df_stats = pd.DataFrame(index=subjects, columns=stats_cols, dtype=float)
    df_stats.index.name = 'Subject_ID' 

    for subj_id in subjects:
        for condition in CONDITIONS:
            for seg_name, (duration, offset) in SUB_SEGMENTS.items():
                
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

    return df_stats


if __name__ == "__main__":
    file_path = "../GSR_RawData.xlsx"
    sheet_to_load = "T1"
    sheet_time = "timing_1"
    timing = timing_to_dataframe(file_path,sheet_time)
    data = GSR_to_dataframe(file_path,sheet_to_load)

    mean = avg_by_event_and_id("neut1",18,timing,data,30)
    print("{:.10f}".format(mean))





