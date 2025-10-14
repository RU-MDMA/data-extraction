import extract_block

class HRPipeline:
    def __init__(self, root_dir):
        self.root = root_dir


if __name__ == "__main__":
    pipeline = HRPipeline("/Users/jasmineerell/Documents/CS-second-year/MDMA/data/meta_data.csv")
    real_time_meta_data = extract_block.create_block(pipeline.root)