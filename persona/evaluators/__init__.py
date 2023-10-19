from persona.evaluators.base import BaseEvaluator
from persona.evaluators.bbh import BBHEvaluator
from persona.evaluators.mbpp import MBPPEvaluator
from persona.evaluators.mmlu import MMLUEvaluator

def get_evaluator(evaluator_name:str, **args) -> BaseEvaluator:
    if "mmlu" in evaluator_name:
        evaluator = MMLUEvaluator(**args)
    elif "arc" in evaluator_name.lower():
        #Piggyback on MMLU for now (might add ARC-specific evaluator later to deal with the grades)
        evaluator = MMLUEvaluator(**args)
    elif "bbh" in evaluator_name:
        task_name = evaluator_name.split("-")[1].strip()
        evaluator = BBHEvaluator(task_name=task_name, **args)
    elif evaluator_name == "mbpp":
        evaluator = MBPPEvaluator(**args)
    else:
        raise ValueError(f"{evaluator_name} is not supported")

    return evaluator
