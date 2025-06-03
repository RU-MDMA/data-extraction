import extarctData
import DataAnalyzing
import os

import md
import process


class HRPipeline:
    def __init__(self, root_dir):
        self.root = root_dir


if __name__ == "__main__":

    pipeline = HRPipeline("C:/Users/97254/Downloads/DATA")
    meta_path = extarctData.metaDataCsvCreator(pipeline.root)
    # DataAnalyzing.analyze(meta_path)
    md.analyze(meta_path)
    process.execute()

