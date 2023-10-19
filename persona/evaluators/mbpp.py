import argparse
import func_timeout
import json
import os
import re
from tqdm import tqdm

from persona.evaluators.base import BaseEvaluator

code_prompt = \
"""import math
from math import *
{imports}

{code}

{tests}"""

class MBPPEvaluator(BaseEvaluator):
    def __init__(self, timeout=10, **kwargs):
        super().__init__(**kwargs)
        self._timeout = timeout

    def _extract_code(self, prediction):
        pattern = r"```python(.*?)```"
        match = re.search(pattern, prediction, re.DOTALL)

        if match:
            # print("Found a ChatGPT-style code block")
            extracted_func = match.group(1).strip()
            # print(extracted_func)
            prediction = extracted_func
            return prediction
        else:
            # print("No code block found -- returning the whole prediction")
            return prediction

    def _execute_code(self, code: str):
        try:
            locs = {}
            exec(code, locs, locs)
            return 1 # Code ran successfully
        except AssertionError as e:
            print(e)
            return 0 # Assertion failed
        except Exception as e:
            print(e)
            return -1 # Code had some other error

    def construct_test(self, imports, prediction, tests):
        code = self._extract_code(prediction)
        if (code == "") or (code is None):
            return None

        imports_str = '\n'.join(imports)
        tests_str = '\n'.join(tests)

        return code_prompt.format(imports=imports_str, code=code, tests=tests_str)

    def run_test(self, imports, prediction, tests):
        '''Returns: status is an integer indicating the status of the code execution
        1: Code ran successfully
        -1: Code had some other error
        0: Assertion failed
        -2: Code couldn't be extracted
        -3: Code timed out
        '''
        code = self.construct_test(imports, prediction, tests)
        if (code == "") or (code is None):
            status = -2 # Code couldn't be extracted
        else:
            # try to run the code
            try:
                status = func_timeout.func_timeout(self._timeout, self._execute_code, args=(code,))
            except func_timeout.FunctionTimedOut:
                print(f"CAUTION: The code execution timed out (allowed time: {self._timeout}s)")
                status = -3 # Code timed out

        return status
    
    def evaluate(self, preds_path, out_path=None):
        """Evaluate the model."""
        print(f'Evaluating {preds_path}')

        with open(preds_path, 'r') as f:
            all_entries = [json.loads(line.strip()) for line in f.readlines()]        

        print(f'Finished reading input containing {len(all_entries)} entries')

        labeled_instances = []

        correct_count = 0
        empty_prediction_count = 0
        assert_failure_count = 0
        other_failure_count = 0
        extraction_failure_count = 0
        timeout_count = 0

        for instance in tqdm(all_entries):
            predictions = instance['predicted_explanations']
            if len(predictions) == 0:
                empty_prediction_count += 1
                instance['extracted_code'] = ""
                instance['code_status'] = ""
                instance['is_correct'] = False
                labeled_instances.append(instance)
                continue

            code = self._extract_code(predictions[0])
            if (code == "") or (code is None):
                code = ""

            instance['extracted_code'] = code

            imports = instance['imports']
            tests = instance['tests']

            run_status = self.run_test(imports, predictions[0], tests)
            instance['run_status'] = run_status

            if run_status == 1:
                instance['is_correct'] = True
                correct_count += 1
            else:
                instance['is_correct'] = False

                if run_status == 0:
                    assert_failure_count += 1
                elif run_status == -1:
                    other_failure_count += 1
                elif run_status == -2:
                    extraction_failure_count += 1
                elif run_status == -3:
                    timeout_count += 1
                else:
                    print(f'Unknown code execution status: {run_status}')

            labeled_instances.append(instance)

        print(f'Number of empty preditions: {empty_prediction_count}')
        print(f'Number of assertion failures: {assert_failure_count}')
        print(f'Number of extraction failures: {extraction_failure_count}')
        print(f'Number of other failures: {other_failure_count}')
        print(f'Number of timeouts: {timeout_count}')

        accuracy = (correct_count * 1.0) / len(all_entries)
        print(f'Accuracy: {accuracy}')

        if not out_path:
            out_path = os.path.join(os.path.dirname(preds_path), os.path.basename(preds_path).replace('.jsonl', '_labeled.jsonl'))

        with open(out_path, 'w') as f:
            for instance in labeled_instances:
                f.write(json.dumps(instance) + '\n')

        return {'accuracy': accuracy}

parser = argparse.ArgumentParser()
parser.add_argument('--eval_path', help='Path to the file with the predictions', type=str)
parser.add_argument('--output_path', help='Path for the output file', type=str)

if __name__ == "__main__":
    args = parser.parse_args()
    print('\n'.join([f'{k}: {v}' for k, v in vars(args).items()]))

    evaluator = MBPPEvaluator()
    evaluator.evaluate(preds_path=args.eval_path, out_path=args.output_path)
