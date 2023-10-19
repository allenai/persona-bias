NUMBERED_SELECTION_USER_TEMPLATE = """Answer the given multiple choice question and show your work. The answer can only be an option like (A), (B), (C), (D). You need to output the answer in your final sentence like "Therefore, the answer is ...".

Question: {question}"""

NON_NUMBERED_SELECTION_USER_TEMPLATE = """Answer the given multiple choice question and show your work. The answer can only be one of the provided options. You need to output the answer in your final sentence like "Therefore, the answer is ...".

Question: {question}"""

NON_SELECTION_USER_TEMPLATE = """Answer the given question and show your work. You need to output the answer in your final sentence like "Therefore, the answer is ...".

Question: {question}"""

YES_NO_GENERATION_USER_TEMPLATE = """Answer the given multiple choice question and show your work. The answer can only be one of the provided options. You need to output the answer in your final sentence like "Therefore, the answer is ...".

Question: {question}
Options:
- Yes
- No"""

MATH_GENERATION_USER_TEMPLATE = """Answer the given multiple choice question and show your work. The answer can only be a numerical value like 0.1, do not include any symbols and units. You need to output the answer in your final sentence like "Therefore, the answer is ...".

Question: {question}"""

USER_PROMPT_TEMPLATE_MAP = {
    "default": NON_SELECTION_USER_TEMPLATE,

    ##### Option selection (Numbered) #####
    "date_understanding": NUMBERED_SELECTION_USER_TEMPLATE,
    "disambiguation_qa": NUMBERED_SELECTION_USER_TEMPLATE,
    "geometric_shapes": NUMBERED_SELECTION_USER_TEMPLATE,
    "hyperbaton": NUMBERED_SELECTION_USER_TEMPLATE,
    "logical_deduction_three_objects": NUMBERED_SELECTION_USER_TEMPLATE,
    "logical_deduction_five_objects": NUMBERED_SELECTION_USER_TEMPLATE,
    "logical_deduction_seven_objects": NUMBERED_SELECTION_USER_TEMPLATE,
    "movie_recommendation": NUMBERED_SELECTION_USER_TEMPLATE,
    "penguins_in_a_table": NUMBERED_SELECTION_USER_TEMPLATE,
    "reasoning_about_colored_objects": NUMBERED_SELECTION_USER_TEMPLATE,
    "ruin_names": NUMBERED_SELECTION_USER_TEMPLATE,
    "salient_translation_error_detection": NUMBERED_SELECTION_USER_TEMPLATE,
    "snarks": NUMBERED_SELECTION_USER_TEMPLATE,
    "temporal_sequences": NUMBERED_SELECTION_USER_TEMPLATE,
    "tracking_shuffled_objects_three_objects": NUMBERED_SELECTION_USER_TEMPLATE,
    "tracking_shuffled_objects_five_objects": NUMBERED_SELECTION_USER_TEMPLATE,
    "tracking_shuffled_objects_seven_objects": NUMBERED_SELECTION_USER_TEMPLATE,

    ### Option selection (Un-numbered) ####
    "causal_judgement": NON_NUMBERED_SELECTION_USER_TEMPLATE, #Yes/No
    "formal_fallacies": NON_NUMBERED_SELECTION_USER_TEMPLATE, #Valid / Invalid
    "navigate": NON_NUMBERED_SELECTION_USER_TEMPLATE, #Yes/No

    ### Bounded generation ####
    "boolean_expressions": NON_SELECTION_USER_TEMPLATE, #True/False
    "sports_understanding": YES_NO_GENERATION_USER_TEMPLATE, #Yes/No
    "web_of_lies": YES_NO_GENERATION_USER_TEMPLATE, #Yes/No

    ### Unbounded generation ####
    "dyck_languages": NON_SELECTION_USER_TEMPLATE, 
    "multistep_arithmetic_two": MATH_GENERATION_USER_TEMPLATE, 
    "object_counting": MATH_GENERATION_USER_TEMPLATE, 
    "word_sorting": NON_SELECTION_USER_TEMPLATE
}