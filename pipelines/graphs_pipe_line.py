import block_to_graph
import block_creator


class GraphsPipeline:
    def __init__(self, block_path, parameter):
        self.block_path = block_path
        self.parameter = parameter


if __name__ == "__main__":
    pipeline = GraphsPipeline(root_dir = "/Users/jasmineerell/Documents/CS-second-year/MDMA/data/block.csv", parameter= "Mean HR")
    block_to_graph.generate_graphs_for_all_subjects(pipeline.block_path, pipeline.parameter, output_dir="..")