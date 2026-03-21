import os
from Meta_data_creator import metaDataCsvCreator
from block_creator import create_block
from block_to_graph import generate_graphs_for_all_subjects


class AllPipeline:
    VALID_FEATURES = [
        "PNS index", "SNS index", "Stress index", "EE activity", "Intensity",
        "Load", "VO2", "Mean RR", "SDNN", "Mean HR", "SD HR", "Min HR",
        "Max HR", "RMSSD", "NNxx", "pNNxx", "HRVti", "TINN", "DC", "DCmod",
        "AC", "ACmod", "VLF peak", "LF peak", "HF peak", "VLF power",
        "LF power", "HF power", "LF/HF ratio", "RESP", "SD1", "SD2",
        "SD2/SD1", "ApEn", "SampEn", "DFA a1", "DFA a2"
    ]

    def __init__(self, data_path):
        self.data_path = data_path

    def doesTheFileExist(self, file_path):
        return os.path.isfile(file_path)

    def createMetaData(self):
        print("Creating meta data...")
        metaDataCsvCreator(self.data_path)

        meta_path = os.path.join(self.data_path, "meta_data.csv")
        return meta_path if self.doesTheFileExist(meta_path) else None

    def createBlock(self, meta_path):
        print("Creating block...")

        if not meta_path or not self.doesTheFileExist(meta_path):
            print("Meta data missing")
            return None

        create_block(meta_path)
        block_path = os.path.join(self.data_path, "block.csv")

        return block_path if self.doesTheFileExist(block_path) else None

    def createGraphs(self, feature, block_path):
        print("Creating graphs...")

        if feature not in self.VALID_FEATURES:
            print("Invalid feature")
            return None

        if not block_path or not self.doesTheFileExist(block_path):
            print("Block missing")
            return None

        safe_feature = feature.replace(" ", "_").replace("/", "_")
        graphs_dir = os.path.join(self.data_path, f"{safe_feature}_graphs")

        generate_graphs_for_all_subjects(block_path, feature, graphs_dir)

        if os.path.isdir(graphs_dir) and any(f.endswith(".png") for f in os.listdir(graphs_dir)):
            print("Graphs saved to:", graphs_dir)
            return graphs_dir

        print("Graphs failed")
        return None

    def run(self, feature):
        meta_path = self.createMetaData()
        if not meta_path:
            return None

        block_path = self.createBlock(meta_path)
        if not block_path:
            return None

        return self.createGraphs(feature, block_path)


