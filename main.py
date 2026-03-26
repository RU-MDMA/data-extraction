from pipelines.all_pipeline import AllPipeline
from pipelines.graphs_pipeline import GraphsPipeline
import os

def main():

    print("-" * 60)
    print("🚀 PIPELINE SELECTION")
    print("Please choose which process you want to run:")
    print("-" * 20)
    print("• Type 'all':    If this is your FIRST time running the code, or if you")
    print("                 have added/changed data in the source folder.")
    print("• Type 'graphs': If you have already run the code before (results file exists)")
    print("                 and you only want to generate new graphs for different metrics.")
    print("-" * 60)

    choice = input("Choose pipeline (all/graphs): ").strip().lower()

    options = [
        "PNS index", "SNS index", "Stress index", "EE activity", "Intensity",
        "Load", "VO2", "Mean RR", "SDNN", "Mean HR", "SD HR", "Min HR",
        "Max HR", "RMSSD", "NNxx", "pNNxx", "HRVti", "TINN", "DC", "DCmod",
        "AC", "ACmod", "VLF peak", "LF peak", "HF peak", "VLF power",
        "LF power", "HF power", "LF/HF ratio", "RESP", "SD1", "SD2",
        "SD2/SD1", "ApEn", "SampEn", "DFA a1", "DFA a2"
    ]

    print("Available features:", ", ".join(options))
    feature = input("Enter feature name from the list above: ").strip()

    if choice == "all":
        example = r"C:\path\to\folder" if os.name == 'nt' else "/path/to/folder"
        data_path = input(f"Please enter the full path to the folder containing the participants' data. (e.g., {example}): ").strip()
        pipeline = AllPipeline(data_path)

    elif choice == "graphs":
        block_path = input("Enter segments data (csv file) path: ").strip()
        pipeline = GraphsPipeline(block_path, feature)

    else:
        print("Invalid choice. Please choose 'all' or 'graphs'.")
        return

    result = pipeline.run(feature)

    if result:
        print("Pipeline completed successfully.")
        print("Output path:", result)
    else:
        print("Pipeline failed.")


if __name__ == "__main__":
    main()
