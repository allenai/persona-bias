import json
import os

class BaseDataset:
    stop_condition = ["Question:"]

    def __init__(self):
        self._data = []

    def get_data(self):
        return self._data

    def initialize(self, dataset_path, need_ids=False):
        self._initialize_from_jsonl(dataset_path, need_ids)

    def _initialize_from_jsonl(self, dataset_path, need_ids=False):
        """Initialize the dataset from a standarizd jsonl file
        """
        self._data = self._load_jsonl(dataset_path, need_ids)

    def _load_jsonl(self, dataset_path, need_ids=False):
        if (not dataset_path) or (not os.path.exists(dataset_path)):
            raise ValueError(f"Invalid dataset path: {dataset_path}")

        print(f"Loading data from {dataset_path}")

        with open(dataset_path, "r", encoding='utf-8') as in_file:
            dataset = [json.loads(line.strip()) for line in in_file.readlines()]

        if need_ids:
            print("Generating and appending instance ids")
            for idx, data in enumerate(dataset):
                data['id'] = idx

        print(f"Loaded {len(dataset)} instances")
        return dataset

if __name__ == "__main__":
    data_path = "" #Add path to data here
    data_processor = BaseDataset()
    data_processor.initialize(data_path)

    data = data_processor.get_data()[:2]
    print(len(data))
    print(data)