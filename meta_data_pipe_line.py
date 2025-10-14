import Meta_data_creator

"Creates the meta data file"

class HRPipeline:
    def __init__(self, root_dir):
        self.root = root_dir
        self.meta_path = None


if __name__ == "__main__":
    pipeline = HRPipeline("/Users/jasmineerell/Documents/CS-second-year/MDMA/data1") #a path to the directory with the data
    meta_path = Meta_data_creator.metaDataCsvCreator(pipeline.root)