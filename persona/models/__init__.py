from importlib import import_module
import os

from persona.models.base import BaseLLM

def is_openai_model(model_name:str) -> bool:
    return ("gpt-3.5-turbo" in model_name) or ("gpt-4" in model_name) or \
        ("text-davinci" in model_name) or ("code-davinci" in model_name)

def is_openai_chat_model(model_name:str) -> bool:
    if "gpt-3.5-turbo-instruct" in model_name:
        return False

    return ("gpt-3.5-turbo" in model_name) or ("gpt-4" in model_name)

def get_model(model_id:str, **model_params) -> BaseLLM:
    try:
        if is_openai_model(model_id):
            module = import_module(f"persona.models.openai_models")
            print("Imported model module:", module.__name__)
            return module.LLM(**model_params)
        else:
            raise ValueError(f"Model {model_id} is not supported yet")
    except ModuleNotFoundError:
        raise ValueError(f"Model implementation not found for {model_id}")


def get_api_key(model_name:str) -> str:
    if is_openai_model(model_name):
        if "OPENAI_KEY" in os.environ:
            return os.environ["OPENAI_KEY"]
        elif "OPENAI_API_KEY" in os.environ:
            return os.environ["OPENAI_API_KEY"]
        else:
            raise ValueError(f"OPENAI_KEY / OPENAI_API_KEY environment variable not found")
    else:
        raise ValueError(f"Model {model_name} is not supported yet")
    
def get_org_id(model_name:str):
    if is_openai_model(model_name):
        return os.getenv("OPENAI_ORG_ID", "")
    else:
        raise ValueError(f"Model {model_name} is not supported yet")
