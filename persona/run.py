'''Make predictions on the dataset using the model.'''
import argparse
from datetime import datetime
import json
import os
import time

from persona.dataset import get_dataset
from persona.evaluators import get_evaluator
from persona.prompts import get_prompt
from persona.models import get_model, get_api_key, get_org_id

parser = argparse.ArgumentParser()
##Dataset
parser.add_argument("--dataset_name", help="The name of the dataset.", default='mmlu-college_biology')
parser.add_argument("--dataset_path", help="Path to the dataset file (overrides the default path for the given dataset_name)", default='')
parser.add_argument("--start_idx", help="The index of the first instance to use", type=int, default=0)
parser.add_argument("--end_idx", help="The index of the last instance to use (-1 indicates dataset length)", type=int, default=-1)

##Model config
parser.add_argument("--api_key", help="The API key to use.", default="")
parser.add_argument("--org_id", help="The OpenAI org id to use.", default="")
parser.add_argument("--model_name", help="The name of the model to use", default="gpt-3.5-turbo-0613")
parser.add_argument("--model_config_path", help="Path to the model config file (overrides the default path for the given model_name)", default="")

##Prompt config
parser.add_argument("--prompt_type", help="Which prompt template to use", default="adopt_identity_accordance")
parser.add_argument("--persona", help="Persona to use", default="a Human")

##Output config
parser.add_argument("--dry_run", help="If true, just output diagnostic information", action="store_true")
parser.add_argument("--cached_path", help="Path to the file that contains cached predictions", default="")
parser.add_argument("--experiment_prefix", help="The unique prefix for the output files", default="")
parser.add_argument("--output_dir", help="Path to the output dir for the experiment", default="results")

##Evaluation config
parser.add_argument("--eval", help="If true, evaluate the predictions", action="store_true")
parser.add_argument("--evaluator_name", help="The name of the evaluator to use (by default, an evaluator with the same name as the dataset name is used)", default="")


if __name__ == "__main__":
	args = parser.parse_args()

	### Print the arguments ###
	###########################
	print("Arguments:")
	for arg_name in vars(args):
		print(f"{arg_name}: {getattr(args, arg_name)}", end="\n")


	### Load Dataset ###
	####################
	dataset_name = args.dataset_name
	dataset_path = None

	if ("mmlu" not in dataset_name) and ("bbh" not in dataset_name) \
		and ("arc" not in dataset_name) and (dataset_name != 'mbpp'): # we load MMLU, BBH, ARC, MBPP directly from HF datasets
		if args.dataset_path:
			dataset_path = args.dataset_path
		else:
			if dataset_name != "default":
				dataset_path = f"data/{dataset_name}/test.jsonl"
			else:
				raise ValueError(f"Unable to figure out the dataset path. Provided path: {args.dataset_path}, Provided dataset name {args.dataset_name}")

		if not os.path.isfile(dataset_path):
			raise ValueError(f"Dataset path {dataset_path} does not exist.")
		else:
			print(f"Loading dataset from {dataset_path}...")

	if ("arc" in dataset_name) and ("_" in dataset_name):
		#arc-challenge_3_4_5
		grades = [grade.strip() for grade in dataset_name.split("_")[1:]]
		partition = dataset_name.split("_", 1)[0]
		dataset = get_dataset(partition, dataset_path, keep_grades=set(grades))
	else:
		dataset = get_dataset(dataset_name, dataset_path)

	# Only keep the instances between a given start and end index
	start_idx = args.start_idx
	end_idx = args.end_idx

	test_set = dataset.get_data()
	if start_idx > 0 or end_idx > 0:
		if (end_idx < 0) or (end_idx > len(test_set)):
			end_idx = len(test_set)

		test_set = test_set[start_idx:end_idx]

	print(f"Using {len(test_set)} instances from the dataset ({start_idx} to {end_idx})")
	print(f"First instance: {test_set[0]}")

	### Initialize Model ###
	########################
	model_config_path = args.model_config_path
	model_name = args.model_name

	if not (args.model_config_path):
		print(f"No model config path provided. Using default config for {model_name}")
		model_config_path = f"configs/{model_name}/default.json"
	
	if os.path.isfile(model_config_path):
		print(f"Loading model config from {model_config_path}")

		with open(model_config_path, "r") as fr:
			model_params = json.load(fr)

		if model_params["model_name"] != model_name:
			print(f"WARNING!!! model name in the config file ({model_params['model_name']}) does not match the provided model name ({model_name})")
			print(f"Using the provided model name ({model_name})")
			model_params["model_name"] = model_name
	else:
		raise ValueError(f"Model config path {model_config_path} does not exist.")

	if args.api_key:
		model_params["api_key"] = args.api_key
	else:
		model_params["api_key"] = get_api_key(model_name)
	
	if args.org_id:
		model_params["org_id"] = args.org_id
	else:
		org_id = get_org_id(model_name)
		if org_id:
			model_params["org_id"] = org_id

	model = get_model(model_name, **model_params)
	print(f"Done initializing model: {model.get_name()}")
	print("Model params:")
	for param_name in model_params:
		print(f"{param_name}: {model_params[param_name]}")

	### Set up the prompt ###
	#########################
	prompt_type = args.prompt_type
	persona = args.persona

	prompt_dict = get_prompt(dataset_name, model_name, prompt_type, persona)

	print("Done setting up the prompts.")
	print(f"System prompt: {prompt_dict['system_prompt']}", end="\n\n")
	print(f"User prompt: {prompt_dict['user_prompt']}")

	### Set up output path ###
	##########################
	now = datetime.now()
	dt_string = now.strftime("%mm-%dd_%Hh-%Mm_%Ss_%fms")

	if "mmlu" in dataset_name:
		task_name = dataset_name.split("-")[1].strip()
		output_dir = f"results/mmlu/{model_name}/{prompt_type}/{task_name}"
	elif "bbh" in dataset_name:
		task_name = dataset_name.split("-")[1].strip()
		output_dir = f"results/bbh/{model_name}/{prompt_type}/{task_name}"
	elif "arc" in dataset_name:
		partition = dataset_name
		grades = "all"

		if "_" in dataset_name:
			partition = dataset_name.split("_", 1)[0].strip()
			grades = dataset_name.split("_", 1)[1].strip()
		output_dir = f"results/{partition}/{model_name}/{prompt_type}/{grades}"
	else:
		output_dir = f"results/{dataset_name}/{model_name}/{prompt_type}"

	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	print(f"Saving results to {output_dir}")
	if args.experiment_prefix:
		persona = persona.replace(" ", "_")
		raw_output_path = f"{output_dir}/{args.experiment_prefix}_{persona}_raw_responses_s{start_idx}_e{end_idx}_temp{model_params['temperature']}_gen{model_params['num_samples']}_{dt_string}.jsonl"
		text_output_path = f"{output_dir}/{args.experiment_prefix}_{persona}_text_predictions_s{start_idx}_e{end_idx}_temp{model_params['temperature']}_gen{model_params['num_samples']}_{dt_string}.jsonl"
	else:
		persona = persona.replace(" ", "_")
		raw_output_path = f"{output_dir}/{persona}_raw_responses_s{start_idx}_e{end_idx}_temp{model_params['temperature']}_gen{model_params['num_samples']}_{dt_string}.jsonl"
		text_output_path = f"{output_dir}/{persona}_text_predictions_s{start_idx}_e{end_idx}_temp{model_params['temperature']}_gen{model_params['num_samples']}_{dt_string}.jsonl"

	print(f"Saving raw response to {raw_output_path}")
	print(f"Saving text predictions to {text_output_path}")

	### Load cached predictions ###
	###############################
	cached_set = dict()
	if args.cached_path:
		with open(args.cached_path, 'r') as f:
			for line in f:
				line = line.strip()
				cached_set[json.loads(line)['id']] = line

			print(f"Loaded {len(cached_set)} cached predictions from {args.cached_path}")
	else:
		print("No cached predictions provided. Starting from scratch...")

	### Make Predictions ###
	########################
	print(f"Making predictions now ...")

	num_cache_hits = 0
	num_api_errors = 0
	prompt_tokens_used = 0
	completion_tokens_used = 0
	total_tokens_used = 0

	t0 = time.time()
	with open(raw_output_path, 'w', encoding='utf-8') as raw_writer, \
		open(text_output_path, 'w', encoding='utf-8') as text_writer:

		for i, instance in enumerate(test_set):
			question_id = instance["id"]

			if question_id in cached_set:
				# Skip if we already have a prediction for this instance
				num_cache_hits += 1
				text_writer.write(cached_set[question_id].strip("\n") + "\n")
				continue
			
			question = instance["question"]
			if dataset_name == "mbpp":
				system_prompt = prompt_dict["system_prompt"]
				user_prompt = prompt_dict["user_prompt"]
				user_prompt_builder = prompt_dict["user_prompt_builder"]
				user_prompt = user_prompt_builder(user_prompt=user_prompt, question=question, tests=instance["tests"])
			else:
				system_prompt = prompt_dict["system_prompt"]
				user_prompt = prompt_dict["user_prompt"]
				user_prompt = user_prompt.format(question=question)

			if args.dry_run:
				print(f"System prompt: {system_prompt}")
				print(f"User prompt: {user_prompt}")
				print('=======================')
				continue

			raw_response = model.generate(user_prompt=user_prompt, system_prompt=system_prompt, stop_condition=dataset.stop_condition, idx=question_id) # type: ignore

			if raw_response is None:
				raw_response = ""
				num_api_errors += 1
			
			model.add_usage(raw_response)

			raw_out_data = {
				"id": question_id,
				"system_prompt": system_prompt,
				"user_prompt": user_prompt,
				"raw_response": raw_response
			}

			raw_writer.write(json.dumps(raw_out_data) + "\n")

			text_responses = model.extract_text(raw_response)
			instance['predicted_explanations'] = text_responses

			text_writer.write(json.dumps(instance) + "\n")

			if (i + 1) % 10 == 0:
				print(f"Finished {i + 1} examples", flush=True)

	print(f"Finished {len(test_set)} examples", flush=True)
	print(f"Number of cache hits: {num_cache_hits}", flush=True)
	print(f"Number of API errors: {num_api_errors}", flush=True)

	model.print_usage(len(test_set))

	seconds_taken = time.time() - t0
	print(f"Total time taken: {seconds_taken // 3600}:{(seconds_taken % 3600) // 60}:{seconds_taken % 60} seconds.", flush=True)
	print(f"Average time per example: {seconds_taken / len(test_set)} seconds.", flush=True)

	if args.eval:
		print("\n\n ...................... \n\n")
		print("Evaluating predictions ...")

		if args.evaluator_name:
			evaluator_name = args.evaluator_name
		else:
			evaluator_name = dataset_name

		print(f"Using the evaluator: {evaluator_name}")
		evaluator = get_evaluator(evaluator_name)

		evaluator.evaluate(text_output_path)
