from all_pipeline import AllPipeline
from graphs_pipeline import GraphsPipeline


def main():
    choice = input("Choose pipeline (all/graphs): ").strip().lower()
    feature = input("Enter feature name: ").strip()

    if choice == "all":
        data_path = input("Enter data directory path: ").strip()
        pipeline = AllPipeline(data_path)

    elif choice == "graphs":
        block_path = input("Enter block.csv path: ").strip()
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
