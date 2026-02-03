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
        flag = self.doesTheFileExcist(self.data_path, "meta_data.csv")
        if flag:
            print("Created meta data file in the given data directory")
        else:
            print("Did not created meta data file")

    def doesTheFileExcist(self,file_dir,file_end):
        flag = os.path.join(file_dir, file_end)
        return flag

    def createBlock(self, meta_data_path):
        if not self.doesTheFileExcist(self.data_path, "meta_data.csv"):
            print("No meta data file to create block from")
        else:
            create_block(meta_data_path)
            #if doesTheFileExcist(self.data_path, "")









if __name__ == "__main__":
    dataPath = "/Users/jasmineerell/Documents/CS-second-year/MDMA/data"
    pipeLine = allPipeLine(dataPath)
    pipeLine.createMetaData()
    pipeLine.createBlock("/Users/jasmineerell/Documents/CS-second-year/MDMA/data/meta_data.csv")