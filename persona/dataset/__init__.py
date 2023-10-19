from persona.dataset.base import BaseDataset
from persona.dataset.bbh import BBH
from persona.dataset.mbpp import MBPP
from persona.dataset.mmlu import MMLU

def get_dataset(dataset_name:str, dataset_path = None, **args) -> BaseDataset:
    if "mmlu" in dataset_name:
        task_name = dataset_name.split("-")[1].strip()
        print(f"Using the MMLU task of: {task_name}")
        dataset = MMLU(task_name, **args)
        dataset.initialize()
    elif "bbh" in dataset_name:
        task_name = dataset_name.split("-")[1].strip()
        print(f"Using the BBH task of: {task_name}")
        dataset = BBH(task_name, **args)
        dataset.initialize()
    elif dataset_name.lower() == "mbpp":
        dataset = MBPP(**args)
        dataset.initialize()
    elif dataset_name == "default":
        dataset = BaseDataset()
        dataset.initialize(dataset_path, **args)
    else:
        raise ValueError(f"{dataset_name} is not supported")

    return dataset
