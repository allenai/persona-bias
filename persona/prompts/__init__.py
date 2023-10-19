from importlib import import_module
from persona.models import is_openai_chat_model, is_openai_model

def get_prompt(dataset_name:str, model_name:str, prompt_type:str, persona:str) -> dict:
    try:
        if is_openai_model(model_name):
            if prompt_type == "no_persona":
                system_prompt = ""
            else:
                system_prompt_module = import_module(f"persona.prompts.{prompt_type}_system_prompt")
                print("Imported system prompt module:", system_prompt_module.__name__)
                system_prompt = system_prompt_module.SYSTEM_PROMPT_TEMPLATE
                system_prompt = system_prompt.format(persona=persona)

            dataset_module_name = get_dataset_module_name(dataset_name)
            user_prompt_module = import_module(f"persona.prompts.{dataset_module_name}.user_prompt")
            print("Imported user prompt module:", user_prompt_module.__name__)

            user_prompt_builder = None

            if dataset_module_name == "bbh":
                task_name = dataset_name.split("-")[1].strip()
                if task_name in user_prompt_module.USER_PROMPT_TEMPLATE_MAP:
                    user_prompt = user_prompt_module.USER_PROMPT_TEMPLATE_MAP[task_name]
                else:
                    print(f"CAUTION: Task {task_name} not found in the user prompt map. Using the default prompt.")
                    user_prompt = user_prompt_module.USER_PROMPT_TEMPLATE_MAP["default"]
            elif dataset_module_name == "mbpp":
                user_prompt = user_prompt_module.USER_PROMPT_TEMPLATE
                user_prompt_builder = user_prompt_module.user_prompt_builder
            else:
                user_prompt = user_prompt_module.USER_PROMPT_TEMPLATE

            if not is_openai_chat_model(model_name):
                user_prompt = f"{system_prompt}\n\n{user_prompt}"
                system_prompt = ""

            return {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "user_prompt_builder": user_prompt_builder
            }
        else:
            raise ValueError(f"Only OpenAI models are supported at the moment. Provided model: {model_name}")
    except ModuleNotFoundError:
        raise ValueError(f"Prompt {prompt_type} is not supported for dataset {dataset_name}, model {model_name}")


def get_dataset_module_name(dataset_name):
    if "mmlu" in dataset_name:
        # Remove the task qualifiers such as mmlu-abstract_algebra
        dataset_module_name = "mmlu"
    elif "bbh" in dataset_name:
        # Remove the task qualifiers such as bbh-tracking_shuffled_objects_five_objects
        dataset_module_name = "bbh"
    else:
        dataset_module_name = dataset_name
    
    return dataset_module_name