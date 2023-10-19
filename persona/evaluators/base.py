"""Base class for evaluators."""
import json
import os
from tqdm import tqdm

class BaseEvaluator:
    """Base class for evaluators."""

    def _extract_answer(self, prediction:str):
        """Override this method to extract the answer from the explanation"""
        raise NotImplementedError("This method should be implemented in the child class")

    def _normalize(self, text):
        """Override this method to normalize the strings before comparing them."""
        raise NotImplementedError("This method should be implemented in the child class")

    def _check_equal(self, instance:dict):
        """Override this method to compare the prediction against the reference (instance is a dictionary that contains both )"""
        raise NotImplementedError("This method should be implemented in the child class")

    def evaluate(self, preds_path, out_path=None):
        """Evaluate the model."""
        print(f'Evaluating {preds_path}')

        with open(preds_path, 'r') as f:
            all_entries = [json.loads(line.strip()) for line in f.readlines()]        

        print(f'Finished reading input containing {len(all_entries)} entries')

        labeled_instances = []

        empty_prediction_count = 0
        extraction_failure_count = 0
        correct_count = 0

        for instance in tqdm(all_entries):
            # gt = instance['answer']
            # answer_type = instance['answer_type']

            predictions = instance['predicted_explanations']
            if len(predictions) == 0:
                empty_prediction_count += 1
                instance['predicted_answer'] = ""
                instance['is_correct'] = False
                labeled_instances.append(instance)
                continue

            # Caution: Some of the normalized predictions can be None
            predicted_answers = [self._extract_answer(prediction) for prediction in predictions]
            prediction = predicted_answers[0]

            if (prediction is None) or (prediction == ''):
                extraction_failure_count += 1
                instance['predicted_answer'] = ""
                instance['is_correct'] = False
                labeled_instances.append(instance)
                print(f"Extraction failure: {instance['predicted_explanations']}")
                continue

            instance['predicted_answer'] = prediction

            is_correct = self._check_equal(instance)
            instance['is_correct'] = is_correct

            if is_correct:
                correct_count += 1

            labeled_instances.append(instance)

        print(f'Number of empty preditions: {empty_prediction_count}')
        print(f'Number of extraction failure: {extraction_failure_count}')

        accuracy = (correct_count * 1.0) / len(all_entries)
        print(f'Accuracy: {accuracy}')

        if not out_path:
            out_path = os.path.join(os.path.dirname(preds_path), os.path.basename(preds_path).replace('.jsonl', '_labeled.jsonl'))

        with open(out_path, 'w') as f:
            for instance in labeled_instances:
                f.write(json.dumps(instance) + '\n')

        return {'accuracy': accuracy}
