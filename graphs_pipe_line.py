import block_to_graph
import block_creator


class HRPipeline:
    def __init__(self, root_dir, parameter):
        self.root = root_dir
        self.parameter = parameter


if __name__ == "__main__":
    pipeline = HRPipeline(root_dir = "/Users/jasmineerell/Documents/CS-second-year/MDMA/data1/meta_data.csv", parameter= "Mean HR")
    block, temp = block_creator.create_block(pipeline.root)
    block_to_graph.generate_graphs_for_all_subjects(block, pipeline.parameter, output_dir=".")