import random
from datasets import load_dataset

from persona.dataset.base import BaseDataset

class MBPP(BaseDataset):
    #NOTE: We use the mbpp-sanitized version as it is more reliable; mbpp-full has different column names and is not as clean
    def __init__(self, seed=None):
        super().__init__()
        self._seed = seed

    def initialize(self, need_ids=False):
        hf_dataset = load_dataset("mbpp", "sanitized")
        for idx, hf_inst in enumerate(hf_dataset['test']): # type: ignore
            instance = {}
            if need_ids:
                instance['id'] = idx
            else:
                instance['id'] = hf_inst['task_id'] # type: ignore

            instance['question'] = hf_inst['prompt'].strip() # type: ignore
            instance['answer'] = hf_inst['code'].strip() # type: ignore
            instance['imports'] = [imp.strip() for imp in hf_inst['test_imports']] # type: ignore
            instance['tests'] = [test.strip() for test in hf_inst['test_list']] # type: ignore

            self._data.append(instance)

        if self._seed is not None:
            random.seed(self._seed)
            random.shuffle(self._data)


if __name__ == "__main__":
    data_processor = MBPP()
    data_processor.initialize()

    data = data_processor.get_data()
    # Print length distribution of imports
    import_lengths = set(sorted([len(inst['imports']) for inst in data]))
    print(f"Import lengths: {import_lengths}")

    # Print length distribution of tests
    test_lengths = set(sorted([len(inst['tests']) for inst in data]))
    print(f"Test lengths: {test_lengths}")

    data = data_processor.get_data()[:1]
    print(len(data))
    print(data)
    for inst in data:
        print(inst['id'])
        print(inst['question'])
        print(inst['answer'])
        print(inst['imports'])
        print(inst['tests'])
        print()
