import os
import block_to_graph


class GraphsPipeline:
    def __init__(self, block_path, feature):
        self.block_path = block_path

    def doesTheFileExist(self, file_path):
        return os.path.isfile(file_path)

    def run(self,feature):
        print("Running graphs-only pipeline...")

        if not self.block_path or not self.doesTheFileExist(self.block_path):
            print("Block file does not exist")
            return None

        safe_feature = feature.replace(" ", "_").replace("/", "_")
        output_dir = os.path.dirname(self.block_path)
        graphs_dir = os.path.join(output_dir, f"{safe_feature}_graphs")

        block_to_graph.generate_graphs_for_all_subjects(
            self.block_path,
            feature,
            graphs_dir
        )

        if os.path.isdir(graphs_dir) and any(f.endswith(".png") for f in os.listdir(graphs_dir)):
            print("Graphs saved to:", graphs_dir)
            return graphs_dir

        print("Graphs failed")
        return None