import os
import time
import openai

from typing import Union

from persona.models.base import BaseLLM
from persona.models import is_openai_chat_model

API_COSTS = {
    "gpt-3.5-turbo-0613": {
        "input_token": 0.0000015,
        "output_token": 0.000002
    },
    "gpt-4-0613": {
        "input_token": 0.00003,
        "output_token": 0.00006
    }
}

class LLM(BaseLLM):
    def __init__(self, model_name='gpt-3.5-turbo-0613', temperature=0, max_tokens=512, logprobs=None,
                 top_p=1, num_samples=1, max_retries=15, api_key="", org_id=""):
        super().__init__(model_name)

        self._temperature = temperature
        self._max_tokens = max_tokens
        self._logprobs = logprobs
        self._top_p = top_p
        self._num_samples = num_samples
        self._max_retries = max_retries

        if api_key:
            openai.api_key = api_key
        else:
            openai.api_key = os.environ["OPENAI_KEY"]
        
        if org_id:
            openai.organization = org_id
        else:
            org_id = os.getenv("OPENAI_ORG_ID", "")
            if org_id:
                openai.organization = os.environ["OPENAI_ORG_ID"]
            else:
                print("OPENAI_ORG_ID environment variable not found -- using the default on the account")
        
        self._prompt_tokens_used = 0
        self._completion_tokens_used = 0
        self._total_tokens_used = 0


    def generate(self, user_prompt:str, system_prompt:str = "", stop_condition:Union[list, None] = None, idx="") -> Union[dict, None]:
        num_retries = 0
        response = None
        
        got_result = False
        while not got_result:
            try:
                if not is_openai_chat_model(self._model_name):
                    response = openai.Completion.create(
                        model=self._model_name,
                        prompt=user_prompt,
                        temperature=self._temperature,
                        max_tokens=self._max_tokens,
                        top_p=self._top_p,
                        logprobs=self._logprobs,
                        frequency_penalty=0.0,
                        presence_penalty=0.0,
                        stop=stop_condition,
                        n=self._num_samples
                    )
                else:
                    ## Chat models
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]

                    #logprobs was deprecated
                    response = openai.ChatCompletion.create(
                        model=self._model_name,
                        messages=messages,
                        temperature=self._temperature,
                        max_tokens=self._max_tokens,
                        top_p=self._top_p,
                        frequency_penalty=0.0,
                        presence_penalty=0.0,
                        stop=stop_condition,
                        n=self._num_samples
                    )

                got_result = True
            except Exception as e:
                if (num_retries < self._max_retries) or (self._max_retries == -1):
                    wait_time = 5 * (1 + num_retries)
                    print(e)
                    print(f"ID: {idx}. API error; Retry number {1 + num_retries}. Retrying in {wait_time} seconds")
                    time.sleep(wait_time)
                    num_retries += 1
                else:
                    print(e)
                    print("\n\n" + user_prompt)
                    print(f"ID: {idx}. Hit the retry quota. Skipping this instance.")
                    return None

        return response #type: ignore


    def extract_text(self, response, skip_if_trimmed=False) -> list[str]:
        if (response == "") or (response is None):
            return []

        text_responses = []
        for choice in response["choices"]:
            if choice["finish_reason"] != "stop":
                print("Text didn't terminate due to the stop condition (likely due to the length)")
                if skip_if_trimmed:
                    text_responses.append("")
                    continue

            if not is_openai_chat_model(self._model_name):
                text = choice["text"].strip()
            else:
                text = choice["message"]["content"].strip()

            text_responses.append(text)

        return text_responses
    
    def add_usage(self, response):
        '''Extracts the usage information from the response object and tracks it'''
        if response:
            try:
                self._prompt_tokens_used += response['usage']['prompt_tokens']
                self._completion_tokens_used += response['usage']['completion_tokens']
                self._total_tokens_used += response['usage']['total_tokens']
            except KeyError:
                print("Usage information not found in response.")
    

    def calculate_cost(self, input_tokens, output_tokens) -> float:
        '''Calculates the cost of the API call(s)'''
        if self._model_name in API_COSTS:
            input_cost = input_tokens * API_COSTS[self._model_name]["input_token"]
            output_cost = output_tokens * API_COSTS[self._model_name]["output_token"]
        else:
            print(f"Cost information not found for model {self._model_name}.")
            return 0.0

        return input_cost + output_cost


    def print_usage(self, num_instances=1):
        '''Prints the usage information'''
        print(f"Prompt tokens used: {self._prompt_tokens_used}")
        print(f"Completion tokens used: {self._completion_tokens_used}")
        print(f"Total tokens used: {self._total_tokens_used}")

        cost = self.calculate_cost(self._prompt_tokens_used, self._completion_tokens_used)
        print(f"Cost: ${cost}")

        print(f"Avg. Prompt tokens used per instance: {self._prompt_tokens_used / num_instances}")
        print(f"Avg. Completion tokens used per instance: {self._completion_tokens_used / num_instances}")
        print(f"Avg. Total tokens used per instance: {self._total_tokens_used / num_instances}")


if __name__ == "__main__":
    model_name = "gpt-3.5-turbo-0613"

    llm = LLM(model_name=model_name)
    response = llm.generate(user_prompt = "Hello, how are you?")
    text = llm.extract_text(response)
    print(text)
    llm.add_usage(response)
    llm.print_usage()

    system_prompt = "You are a helpful llama."
    user_prompt = "Question: Can Murphy fly?"

    if is_openai_chat_model(model_name):
        response = llm.generate(user_prompt = user_prompt, system_prompt = system_prompt)
    else:
        user_prompt = system_prompt + "\n\n" + user_prompt
        response = llm.generate(user_prompt = user_prompt)

    text = llm.extract_text(response)
    print(text)
    llm.add_usage(response)
    llm.print_usage()
