from datasets import load_dataset

from persona.dataset.base import BaseDataset

class BBH(BaseDataset):
    tasks = {
        ##### Option selection (Numbered) #####
        "date_understanding": "option_numbered",
        "disambiguation_qa": "option_numbered",
        "geometric_shapes": "option_numbered",
        "hyperbaton": "option_numbered",
        "logical_deduction_three_objects": "option_numbered",
        "logical_deduction_five_objects": "option_numbered",
        "logical_deduction_seven_objects": "option_numbered",
        "movie_recommendation": "option_numbered",
        "penguins_in_a_table": "option_numbered",
        "reasoning_about_colored_objects": "option_numbered",
        "ruin_names": "option_numbered",
        "salient_translation_error_detection": "option_numbered",
        "snarks": "option_numbered",
        "temporal_sequences": "option_numbered",
        "tracking_shuffled_objects_three_objects": "option_numbered",
        "tracking_shuffled_objects_five_objects": "option_numbered",
        "tracking_shuffled_objects_seven_objects": "option_numbered",

        ### Option selection (Un-numbered) ####
        "causal_judgement": "option_non_numbered", #Yes/No
        "formal_fallacies": "option_non_numbered", #Valid / Invalid
        "navigate": "option_non_numbered", #Yes/No

        ### Bounded generation ####
        "boolean_expressions": "bounded_generation", #True/False
        "sports_understanding": "bounded_generation", #Yes/No
        "web_of_lies": "bounded_generation", #Yes/No

        ### Unbounded generation ####
        "dyck_languages": "unbounded", 
        "multistep_arithmetic_two": "unbounded", 
        "object_counting": "unbounded", 
        "word_sorting": "unbounded" 
    }

    def __init__(self, task_name):
        super().__init__()
        if task_name not in self.tasks:
            raise ValueError(f"Invalid task name: {task_name}")

        self._task_name = task_name

    def initialize(self, need_ids=True):
        hf_dataset = load_dataset("lukaemon/bbh", self._task_name)
        for idx, hf_inst in enumerate(hf_dataset['test']): # type: ignore
            instance = {}
            if need_ids:
                instance['id'] = idx

            question = hf_inst['input'].strip() # type: ignore

            instance['question'] = question
            instance['answer'] = hf_inst['target'].strip() # type: ignore

            self._data.append(instance)


if __name__ == "__main__":
    task_name = "tracking_shuffled_objects_five_objects"
    data_processor = BBH(task_name)
    data_processor.initialize()

    data = data_processor.get_data()[:2]
    print(len(data))
    print(data)
    for inst in data:
        print(inst['question'])
        print(inst['answer'])
        print()
