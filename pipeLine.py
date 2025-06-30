import extarctData
#import DataAnalyzing
import os
import extract_real_time_meta_data
import real_time_data_to_graph

import md
import process


class HRPipeline:
    def __init__(self, root_dir):
        self.root = root_dir
        self.meta_path = None


if __name__ == "__main__":

    pipeline = HRPipeline("/Users/jasmineerell/Documents/CS-second-year/MDMA/data")

    meta_path = extarctData.metaDataCsvCreator(pipeline.root)
    #DataAnalyzing.analyze(meta_path)
    #md.analyze(meta_path)
    #process.execute()

    parameter = "Mean HR"
    subject_id = 15

    #excel_path, _ = extract_real_time_meta_data.real_time_meta_data("/Users/jasmineerell/Documents/CS-second-year/MDMA/data/meta_data.csv")
    #excel_path = "/Users/jasmineerell/Documents/CS-second-year/MDMA/data/meta_data_real_time_meta_data.csv"
    #real_time_data_to_graph.generate_graphs_for_all_subjects(excel_path, parameter, output_dir = ".")



