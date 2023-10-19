import argparse
import re

from persona.evaluators.base import BaseEvaluator

class MMLUEvaluator(BaseEvaluator):

    def _extract_answer(self, prediction:str):
        if (prediction is None) or (prediction == ''):
            return None
        
        matches = re.findall(r"answer is:?\s*(.*)", prediction, re.IGNORECASE)
        if matches:
            prediction = matches[-1].strip().strip(".")

        prediction = prediction.strip('\n').strip().strip(".")

        match = re.search(r'\(([a-z])\)', prediction, re.IGNORECASE)
        if match:
            return match.group(1)
        else:
            #If these errors are a lot, add support for extracting the answer using ChatGPT
            return None

    def _normalize(self, text):
        return text.replace("(", "").replace(")", "").upper().strip()

    def _check_equal(self, instance) -> bool:
        '''Compare prediction against the reference'''
        gt = self._normalize(instance['answer'])
        pred = self._normalize(instance['predicted_answer'])

        if gt == pred:
            return True
        else:
            return False


parser = argparse.ArgumentParser()
parser.add_argument('--eval_path', help='Path to the file with the predictions', type=str)
parser.add_argument('--output_path', help='Path for the output file', type=str)

if __name__ == "__main__":
    args = parser.parse_args()
    print('\n'.join([f'{k}: {v}' for k, v in vars(args).items()]))

    evaluator = MMLUEvaluator()
    evaluator.evaluate(preds_path=args.eval_path, out_path=args.output_path)
