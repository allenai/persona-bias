from typing import List

USER_PROMPT_TEMPLATE = """Write a python program for the following problem:
"{question}"

Your code should pass these tests:

{tests}"""

def create_tests_string(tests: List[str]) -> str:
    test_string = ""
    for idx, test in enumerate(tests, start=1):
        test_string += f"Test {idx}: \"{test}\"" + "\n"

    test_string = test_string.strip().rstrip("\n")
    return test_string

def user_prompt_builder(template=USER_PROMPT_TEMPLATE, **args) -> str:
    question = args['question']
    tests = args['tests']

    return template.format(question=question, tests=create_tests_string(tests))

