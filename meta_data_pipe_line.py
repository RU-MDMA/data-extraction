import Meta_data_creator
import extract_block

class HRPipeline:
    def __init__(self, root_dir):
        self.root = root_dir
        self.meta_path = None


if __name__ == "__main__":
    pipeline = HRPipeline("/Users/jasmineerell/Documents/CS-second-year/MDMA/data1")
    meta_path = Meta_data_creator.metaDataCsvCreator(pipeline.root)