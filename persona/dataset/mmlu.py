from datasets import load_dataset

from persona.dataset.base import BaseDataset

class MMLU(BaseDataset):
    subcategories = {
        "abstract_algebra": ["math"],
        "anatomy": ["health"],
        "astronomy": ["physics"],
        "business_ethics": ["business"],
        "clinical_knowledge": ["health"],
        "college_biology": ["biology"],
        "college_chemistry": ["chemistry"],
        "college_computer_science": ["computer science"],
        "college_mathematics": ["math"],
        "college_medicine": ["health"],
        "college_physics": ["physics"],
        "computer_security": ["computer science"],
        "conceptual_physics": ["physics"],
        "econometrics": ["economics"],
        "electrical_engineering": ["engineering"],
        "elementary_mathematics": ["math"],
        "formal_logic": ["philosophy"],
        "global_facts": ["other"],
        "high_school_biology": ["biology"],
        "high_school_chemistry": ["chemistry"],
        "high_school_computer_science": ["computer science"],
        "high_school_european_history": ["history"],
        "high_school_geography": ["geography"],
        "high_school_government_and_politics": ["politics"],
        "high_school_macroeconomics": ["economics"],
        "high_school_mathematics": ["math"],
        "high_school_microeconomics": ["economics"],
        "high_school_physics": ["physics"],
        "high_school_psychology": ["psychology"],
        "high_school_statistics": ["math"],
        "high_school_us_history": ["history"],
        "high_school_world_history": ["history"],
        "human_aging": ["health"],
        "human_sexuality": ["culture"],
        "international_law": ["law"],
        "jurisprudence": ["law"],
        "logical_fallacies": ["philosophy"],
        "machine_learning": ["computer science"],
        "management": ["business"],
        "marketing": ["business"],
        "medical_genetics": ["health"],
        "miscellaneous": ["other"],
        "moral_disputes": ["philosophy"],
        "moral_scenarios": ["philosophy"],
        "nutrition": ["health"],
        "philosophy": ["philosophy"],
        "prehistory": ["history"],
        "professional_accounting": ["other"],
        "professional_law": ["law"],
        "professional_medicine": ["health"],
        "professional_psychology": ["psychology"],
        "public_relations": ["politics"],
        "security_studies": ["politics"],
        "sociology": ["culture"],
        "us_foreign_policy": ["politics"],
        "virology": ["health"],
        "world_religions": ["philosophy"],
    }

    categories = {
        "STEM": ["physics", "chemistry", "biology", "computer science", "math", "engineering"],
        "humanities": ["history", "philosophy", "law"],
        "social sciences": ["politics", "culture", "economics", "geography", "psychology"],
        "other (business, health, misc.)": ["other", "business", "health"],
    }

    def __init__(self, task_name):
        super().__init__()
        if task_name not in self.subcategories:
            raise ValueError(f"Invalid task name: {task_name}")

        self._task_name = task_name

    def initialize(self, need_ids=True):
        hf_dataset = load_dataset("lukaemon/mmlu", self._task_name)
        for idx, hf_inst in enumerate(hf_dataset['test']): # type: ignore
            instance = {}
            if need_ids:
                instance['id'] = idx

            question = hf_inst['input'].strip() # type: ignore
            
            options_string = ""
            for key in sorted(hf_inst.keys()): # type: ignore
                if key.strip() in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz":
                    options_string += "\n" + f"({key.upper().strip()}) {hf_inst[key].strip()}" # type: ignore

            if options_string:
                question += "\n" + "Options:" + options_string

            instance['question'] = question
            instance['answer'] = hf_inst['target'].strip() # type: ignore

            self._data.append(instance)
        

if __name__ == "__main__":
    task_name = "abstract_algebra"
    data_processor = MMLU(task_name)
    data_processor.initialize()

    data = data_processor.get_data()[:10]
    print(len(data))
    print(data)
    for inst in data:
        print(inst['question'])
        print(inst['answer'])
        print()
