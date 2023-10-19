import argparse
import re

from persona.dataset.bbh import BBH

from persona.evaluators.base import BaseEvaluator

class BBHEvaluator(BaseEvaluator):
    def __init__(self, task_name):
        super().__init__()
        self._task_name = task_name
        if task_name not in BBH.tasks:
            raise ValueError(f"Invalid task name: {task_name}")
        if BBH.tasks[task_name] == "option_numbered":
            self._use_numbered_selection = True
        else:
            self._use_numbered_selection = False

    def _extract_answer(self, prediction:str):
        if (prediction is None) or (prediction == ''):
            return None

        matches = re.findall(r"answer is:?\s*(.*)", prediction, re.IGNORECASE)
        if matches:
            prediction = matches[-1]

        prediction = prediction.replace("\"", "").strip()
        if self._use_numbered_selection:
            prediction = prediction.strip(".").strip().strip(".").strip("\n").strip().strip(".").strip()

            match = re.search(r'\(([a-z])\)', prediction, re.IGNORECASE)
            if match:
                prediction = match.group(1)
                return prediction
            else:
                #If these errors are a lot, add support for extracting the answer using ChatGPT
                return None
        if self._task_name == "word_sorting":
            prediction = prediction.replace(",", "")

        if (self._task_name == "web_of_lies") or (self._task_name == "sports_understanding"):
            match = re.search(r'(yes|no)', prediction, re.IGNORECASE)
            if match:
                prediction = match.group(1)
        
        if (self._task_name == "multi_step_arithmetic_two") or (self._task_name == "object_counting"):
            match = re.findall(r'(\d+)', prediction, re.IGNORECASE)
            if match:
                prediction = match[-1]

        prediction = prediction.strip(".").strip().strip(".").strip("\n").strip().strip(".").strip()
        return prediction

    def _normalize(self, text):
        if self._use_numbered_selection:
            return text.replace("(", "").replace(")", "").upper().strip()
        else:
            return text.strip().upper()

    def _check_equal(self, instance) -> bool:
        '''Compare prediction against the reference'''
        gt = self._normalize(instance['answer'])
        pred = self._normalize(instance['predicted_answer'])

        if gt == pred:
            return True
        else:
            return False


parser = argparse.ArgumentParser()
parser.add_argument('--task_name', help='Name of the task', type=str)
parser.add_argument('--eval_path', help='Path to the file with the predictions', type=str)
parser.add_argument('--output_path', help='Path for the output file', type=str)

if __name__ == "__main__":
    args = parser.parse_args()
    print('\n'.join([f'{k}: {v}' for k, v in vars(args).items()]))

    evaluator = BBHEvaluator(args.task_name)
    evaluator.evaluate(preds_path=args.eval_path, out_path=args.output_path)
