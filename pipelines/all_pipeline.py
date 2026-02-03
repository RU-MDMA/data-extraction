from Meta_data_creator import metaDataCsvCreator
from block_creator import create_block
from block_to_graph import generate_graphs_for_all_subjects
import os


class allPipeLine:
    def __init__(self, data_path):
        self.data_path = data_path
        self.out_path = data_path

    def createMetaData(self):
        metaDataCsvCreator(self.data_path)

        meta_data_path = os.path.join(self.data_path, "meta_data.csv")

        if os.path.isfile(meta_data_path):
            print("Meta data file in the given data directory")
            return meta_data_path
        else:
            print("No meta data file in the given data directory")
            return None

    def doesTheFileExcist(self, file_path):
        return os.path.isfile(file_path)

    def createBlock(self, meta_data_path):
        if not meta_data_path or not self.doesTheFileExcist(meta_data_path):
            print("No meta data file to create block from")
            return None

        create_block(meta_data_path)
        block_path = os.path.join(self.data_path, "block.csv")
        if os.path.isfile(block_path):
            print("Created block file")
            return block_path
        else:
            print("Block file was not created")
            return None

    def createGraphs(self,feature,block_path):
        if not block_path or not self.doesTheFileExcist(block_path):
            print("No block to create graphs from")
            return None

        features = [
            "PNS index",
            "SNS index",
            "Stress index",
            "EE activity",
            "EE activity",
            "Intensity",
            "Load",
            "VO2",
            "Mean RR",
            "SDNN",
            "Mean HR",
            "SD HR",
            "Min HR",
            "Max HR",
            "RMSSD",
            "NNxx",
            "pNNxx",
            "HRVti",
            "TINN",
            "DC",
            "DCmod",
            "AC",
            "ACmod",
            "VLF peak",
            "LF peak",
            "HF peak",
            "VLF power",
            "LF power",
            "HF power",
            "VLF power",
            "LF power",
            "HF power",
            "VLF power",
            "LF power",
            "HF power",
            "LF power",
            "HF power",
            "LF/HF ratio",
            "RESP",
            "SD1",
            "SD2",
            "SD2/SD1",
            "ApEn",
            "SampEn",
            "DFA a1",
            "DFA a2"
        ]
        if feature not in features:
            print("Invalid feature name")
            return None

        graphs_dir = os.path.join(self.data_path, "graphs")
        generate_graphs_for_all_subjects(block_path, feature, graphs_dir)
        if os.path.isdir(graphs_dir) and any(f.endswith(".png") for f in os.listdir(graphs_dir)):
            print("Graphs saved to:", graphs_dir)
            return graphs_dir
        else:
            print("Graphs were not created correctly")
            return None


if __name__ == "__main__":
    dataPath = "/Users/jasmineerell/Documents/CS-second-year/MDMA/data"
    pipeLine = allPipeLine(dataPath)

    #meta_data_path = pipeLine.createMetaData()
    #block_path = pipeLine.createBlock(meta_data_path)
    block_path = "/Users/jasmineerell/Documents/CS-second-year/MDMA/data/block.csv"
    graphs_path = pipeLine.createGraphs("RMSSD", block_path)
