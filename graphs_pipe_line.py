import real_time_data_to_graph


class HRPipeline:
    def __init__(self, root_dir, parameter):
        self.root = root_dir
        self.parameter = parameter


if __name__ == "__main__":
    pipeline = HRPipeline("/Users/jasmineerell/Documents/CS-second-year/MDMA/data/meta_data_real_time_meta_data.csv","Mean HR")
    real_time_data_to_graph.generate_graphs_for_all_subjects(pipeline.root, pipeline.parameter, output_dir=".")