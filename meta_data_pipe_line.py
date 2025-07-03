import extarctData

class HRPipeline:
    def __init__(self, root_dir):
        self.root = root_dir
        self.meta_path = None


if __name__ == "__main__":
    pipeline = HRPipeline("/Users/jasmineerell/Documents/CS-second-year/MDMA/data")
    meta_path = extarctData.metaDataCsvCreator(pipeline.root)