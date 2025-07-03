import extract_real_time_meta_data

class HRPipeline:
    def __init__(self, root_dir):
        self.root = root_dir


if __name__ == "__main__":
    pipeline = HRPipeline("/Users/jasmineerell/Documents/CS-second-year/MDMA/data")
    real_time_meta_data = extract_real_time_meta_data.real_time_meta_data(pipeline.root)