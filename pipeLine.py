import extarctData
import DataAnalyzing
import os

class HRPipeline:
    def __init__(self, root_dir):
        self.root = root_dir


if __name__ == "__main__":

    pipeline = HRPipeline("C:/Users/jasminee/MDMA/RU-MDMA/test")
    meta_path = extarctData.metaDataCsvCreator(pipeline.root)
    DataAnalyzing.analyze(meta_path)

