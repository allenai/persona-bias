from abc import ABC, abstractmethod

from typing import Union, Tuple

class BaseLLM(ABC):
    def __init__(self, model_name:str):
        self._model_name = model_name

    def get_name(self):
        return self._model_name

    @abstractmethod
    def generate(self) -> Union[dict, None]:
        """Queries the model and returns the response object."""
        raise NotImplementedError("generate() not implemented")

    @abstractmethod
    def extract_text(self, response) -> list[str]:
        """Extracts the text from the response object"""
        raise NotImplementedError("extract_text() not implemented")
    
    @abstractmethod
    def add_usage(self, response):
        """Extracts the usage information from the response object and tracks it"""
        raise NotImplementedError("get_usage() not implemented")
    
    @abstractmethod
    def print_usage(self, num_instances=1):
        """Prints the usage information"""
        raise NotImplementedError("print_usage() not implemented")
