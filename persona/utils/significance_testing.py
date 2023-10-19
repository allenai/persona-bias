import argparse
import json
import numpy as np
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.proportion import binom_test, proportion_confint

def run_mcnemar_test(control_preds, treatment_preds, alpha=0.05):
    # Returns True if the null hypothesis is rejected (i.e. the two models are significantly different), False otherwise
    if len(control_preds) != len(treatment_preds):
        raise ValueError("Length of control and treatment predictions must be the same")

    n11 = sum([(a == 1 and b == 1) for a, b in zip(control_preds, treatment_preds)])
    n00 = sum([(a == 0 and b == 0) for a, b in zip(control_preds, treatment_preds)])

    n10 = sum([(a == 1 and b == 0) for a, b in zip(control_preds, treatment_preds)])
    n01 = sum([(a == 0 and b == 1) for a, b in zip(control_preds, treatment_preds)])
    
    # Constructing the 2x2 contingency table
    contingency_table = np.array([[n11, n10], [n01, n00]])
    print(f"Contingency table: {contingency_table}")

    # Check if any of the cells have a value less than 25
    if np.any(contingency_table < 25):
        # Perform exact McNemar's test
        result = mcnemar(contingency_table, exact=True)
    else:
        result = mcnemar(contingency_table, exact=False)

    # summarize the finding
    print('statistic=%.3f, p-value=%.3f' % (result.statistic, result.pvalue)) # type: ignore
    # interpret the p-value

    if result.pvalue > alpha: # type: ignore
        print('Fail to reject H0 (results are not significant)')
        return False
    else:
        print('Rejected H0 (results are significant)')
        return True

def run_binom_test(control_preds, treatment_preds, type="two-sided", alpha=0.05):
    '''
    type in [‘two-sided’, ‘smaller’, ‘larger’]
    '''
    #Returns True if the null hypothesis is rejected (i.e. the two models are significantly different), False otherwise
    if len(control_preds) != len(treatment_preds):
        raise ValueError("Length of control and treatment predictions must be the same")

    h0_prob = sum(control_preds) / len(control_preds)
    print(f"Null hypothesis probability: {h0_prob}")

    p_value = binom_test(count=sum(treatment_preds), nobs=len(treatment_preds), prop=h0_prob, alternative=type)

    # summarize the finding
    print('p-value=%.3f' % p_value)

    # interpret the p-value
    if p_value > alpha: # type: ignore
        print('Fail to reject H0 (results are not significant))')
        return False
    else:
        print('Rejected H0 (results are significant)')
        return True
    
def run_conf_score_test(control_preds, treatment_preds, method="wilson", alpha=0.05):
    if len(control_preds) != len(treatment_preds):
        raise ValueError("Length of control and treatment predictions must be the same")

    control_correct = sum(control_preds)
    treatment_correct = sum(treatment_preds)

    control_acc = sum(control_preds) / len(control_preds)
    treatment_acc = sum(treatment_preds) / len(treatment_preds)

    control_lower, control_upper = proportion_confint(control_correct, len(control_preds), alpha=alpha, method=method)
    treatment_lower, treatment_upper = proportion_confint(treatment_correct, len(treatment_preds), alpha=alpha, method="wilson")

    print(f"Control Acc: {control_acc}, Control lower: {control_lower}, Control upper: {control_upper}")
    print(f"Treatment Acc: {treatment_acc}, Treatment lower: {treatment_lower}, Treatment upper: {treatment_upper}")

    if control_lower > treatment_upper or treatment_lower > control_upper:
        print("Results are significantly different")
        return True
    else:
        print("Results are not significantly different")
        return False


parser = argparse.ArgumentParser()
parser.add_argument("--control_path", type=str, required=True)
parser.add_argument("--treatment_path", type=str, required=True)
parser.add_argument("--alpha", type=float, default=0.05)
parser.add_argument("--test", type=str, default="mcnemar")

def get_evaluations(path):
    with open(path, "r", encoding='utf-8') as f:
        instances = [json.loads(line.strip()) for line in f.readlines()]
        evals = [1 if instance["is_correct"] else 0 for instance in instances]

    print(f"Loaded {len(evals)} instances from {path}")
    print(f"Accuracy: {sum(evals) / len(evals)}")
    return evals


if __name__ == "__main__":
    args = parser.parse_args()

    control_preds = get_evaluations(args.control_path)
    treatment_preds = get_evaluations(args.treatment_path)

    if args.test == "mcnemar":
        run_mcnemar_test(control_preds, treatment_preds, alpha=args.alpha)
    elif "binom" in args.test:
        if "_" in args.test:
            test_type = args.test.split("_")[1]
            if test_type not in ["two-sided", "smaller", "larger"]:
                raise ValueError(f"Invalid test type: {test_type}")

            run_binom_test(control_preds, treatment_preds, type=test_type)
        else:
            run_binom_test(control_preds, treatment_preds)
    elif args.test == "confint":
        if "_" in args.test:
            test_type = args.test.split("_")[1]
            if test_type not in ["normal", "agresti_coull", "beta", "wilson", "jeffreys", "binom_test"]:
                raise ValueError(f"Invalid test type: {test_type}")

            run_conf_score_test(control_preds, treatment_preds, method=test_type, alpha=args.alpha)
        else:
            run_conf_score_test(control_preds, treatment_preds, alpha=args.alpha)
    else:
        raise ValueError(f"Invalid test type: {args.test}")
