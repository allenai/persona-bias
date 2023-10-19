import argparse
import subprocess
import time
from persona.dataset.mmlu import MMLU

predef_datasets = []
predef_datasets.extend(["college_mathematics", "abstract_algebra"]) ## MMLU - Maths datasets
predef_datasets.extend(["college_physics", "conceptual_physics"]) ## MMLU - Physics datasets
predef_datasets.extend(["college_chemistry", "high_school_chemistry"]) ## MMLU - Chemistry datasets
predef_datasets.extend(["college_computer_science", "computer_security", "machine_learning"]) ## MMLU - Computer Science datasets
predef_datasets.extend(["moral_scenarios", "human_sexuality", "professional_medicine"])

predef_datasets.extend(["professional_law", "professional_accounting", "professional_psychology"])
predef_datasets.extend(["high_school_government_and_politics", "high_school_world_history"])
predef_datasets.extend(["college_biology", "anatomy"])
predef_datasets.extend(["sociology", "logical_fallacies", "management"])
predef_datasets = ["mmlu-" + dataset for dataset in predef_datasets]

predef_datasets.extend(["mbpp"])
predef_datasets.extend(["bbh-sports_understanding"])

predef_persona_map = {
    "shared": [
        "a physically-disabled person", "an able-bodied person", #Disability
        "an Atheist person", "a Religious person", "a Jewish person", "a Christian person", #Religion
        "an Asian person", "a Hispanic person", "an African person", "a Caucasian person", #Race
        "a lifelong Democrat", "a lifelong Republican", "a Donald Trump supporter", "a Barack Obama supporter", #Politics
        "a man", "a woman", #Gender
        "an average human",
        "a human",
    ],

    ## Expertise mitigation Personas
    # "mmlu-high_school_world_history": ["a physically-disabled historian", "an able-bodied historian"],
    # "mmlu-professional_law": ["a physically-disabled lawyer", "an able-bodied lawyer"],
    # "mmlu-college_mathematics": ["a physically-disabled mathematician", "an able-bodied mathematician"],
    # "mmlu-college_physics": ["a physically-disabled physicist", "an able-bodied physicist"],

    # "mmlu-college_physics": ["an Atheist physicist", "a Religious physicist"],
    # "mmlu-high_school_chemistry": ["an Atheist chemist", "a Religious chemist"],
    # "mmlu-machine_learning": ["an Atheist machine learning researcher", "a Religious machine learning researcher"],
    # "mmlu-college_computer_science": ["an Atheist computer scientist", "a Religious computer scientist"],
}

predef_max_size_map = {
    "mmlu-moral_scenarios": 250,
    "mmlu-professional_medicine": 250,
    "gsm8k": 250,
    "mmlu-professional_law": 250,
	"mmlu-professional_accounting": 250,
	"mmlu-professional_psychology": 250
}

# Define the parser
parser = argparse.ArgumentParser()
parser.add_argument("--org_id", help="The OpenAI org id to use.", default="")
parser.add_argument("--datasets", help="Comma-separated list of datasets to use.")
parser.add_argument("--personas", help="Comma-separated list of personas to use.")
parser.add_argument("--use_predef_personas", help="Whether to use predefined personas or not (if set, the commandline personas are ignored)", action="store_true", default=False)
parser.add_argument("--use_predef_datasets", help="Whether to use predefined datasets or not (if set, the commandline datasets are ignored)", action="store_true", default=False)
parser.add_argument("--use_predef_max_size", help="Whether to use predefined max dataset sizes or not (if set, the commandline end_idx is ignored)", action="store_true", default=False)
parser.add_argument("--run_no_persona", help="Whether to run with no_persona or not.", action="store_true", default=False)
parser.add_argument("--prompt_type", help="The prompt type to use for the persona experiments", default='no_persona')

parser.add_argument("--start_idx", help="The index of the first instance to use", type=int, required=False)
parser.add_argument("--end_idx", help="The index of the last instance to use (-1 indicates dataset length)", type=int, required=False)

parser.add_argument("--experiment_prefix", help="The unique prefix for the output files", default="")
parser.add_argument("--out_file_prefix", help="Any prefix for the output results file.", default='')
parser.add_argument("--repeat", help="The number of times to repeat the experiment", type=int, default=1)
parser.add_argument("--model_name", help="The model name to use", default="gpt-3.5-turbo-0613")

if __name__ == "__main__":
    args = parser.parse_args()
    # Print the arguments
    print("Arguments:")
    for arg_name in vars(args):
        print(f"{arg_name}: {getattr(args, arg_name)}", end="\n")

    # Datasets
    if args.use_predef_datasets:
        datasets = predef_datasets
    else:
        datasets = [dataset.strip() for dataset in args.datasets.split(',')]

    print(f"Using datasets: {datasets}")

    # Personas
    dataset_persona_map = {}
    if args.use_predef_personas:
        for dataset in datasets:
            dataset_persona_map[dataset] = []
            dataset_persona_map[dataset].extend(predef_persona_map.get("shared", []))
            dataset_persona_map[dataset].extend(predef_persona_map.get(dataset, []))

            if args.run_no_persona:
                dataset_persona_map[dataset].append("no_persona")

    else:
        if (args.personas is None) and (not args.run_no_persona):
            raise ValueError("No persona has been specified")

        personas = []
        if args.personas is not None:
            personas = [persona.strip() for persona in args.personas.split(',')]

        dataset_persona_map = {}
        for dataset in datasets:
            dataset_persona_map[dataset] = []
            dataset_persona_map[dataset].extend(personas)

            if args.run_no_persona:
                dataset_persona_map[dataset].append("no_persona")


    # Pring dataset_persona_map neatly
    print("Dataset-Persona map:")
    for dataset, personas in dataset_persona_map.items():
        print(f"{dataset}: {personas}")

    # Loop over the personas and launch Python script
    # Run parallelization_factor runs at a time and sleep for sleep_time interval afterwards -- this is needed to avoid the OpenAI API rate limit
    parallelization_factor = 2
    sleep_time = 15 * 60 #15mins. -- might need to increase this as the parallelization factor increases

    for dataset, personas in dataset_persona_map.items():
        print(f"\n\nLaunching Python scripts for dataset: {dataset}")
        print("----------------------------------------------")
        print(f"Personas: {personas}")
        done_personas = 0
        for persona in personas:
            done_personas += 1
            print(f"\nLaunching Python script for dataset: {dataset}, persona: {persona}")

            if persona == "no_persona":
                prompt_type = "no_persona"
                persona = "no_persona"
            else:
                prompt_type = args.prompt_type

            kwargs = {}
            kwargs['dataset_name'] = dataset

            kwargs['prompt_type'] = prompt_type
            kwargs['persona'] = persona
            kwargs['model_name'] = args.model_name

            if args.org_id:
                kwargs['org_id'] = args.org_id

            if args.start_idx is not None:
                kwargs['start_idx'] = args.start_idx

            if args.use_predef_max_size:
                kwargs['end_idx'] = predef_max_size_map.get(dataset, -1)
                print(f"Using max size of {kwargs['end_idx']} for dataset: {dataset}")
            else:
                if args.end_idx is not None:
                    kwargs['end_idx'] = args.end_idx

            if args.experiment_prefix:
                kwargs['experiment_prefix'] = args.experiment_prefix

            if ('end_idx' in kwargs) and (kwargs['end_idx'] != -1):
                output_file = f"{args.prompt_type}_{dataset}_size{kwargs['end_idx']}_{persona.replace(' ', '_')}_{args.model_name}_output.txt"
            else:
                output_file = f"{args.prompt_type}_{dataset}_{persona.replace(' ', '_')}_{args.model_name}_output.txt"

            if args.out_file_prefix:
                output_file = f"{args.out_file_prefix}_{output_file}"

            persona = "\"" + persona + "\"" # add quotes to the persona
            kwargs['persona'] = persona

            args_string = " ".join([f"--{k} {v}" for k, v in kwargs.items()])
            args_string += " --eval"

            for i in range(args.repeat):
                out_file = output_file
                if args.repeat > 1:
                    out_file = output_file.replace(".txt", f"_r{i}.txt")

                command = f"nohup python -u persona/run.py {args_string} > {out_file} 2>&1 &"
                print(f"Run number: {i+1}")
                print(f"Command: {command}")
                subprocess.Popen(command, shell=True)
                time.sleep(3)

            if done_personas % parallelization_factor == 0:
                print(f"Done with {done_personas} personas for the dataset: {dataset}")
                print(f"Sleeping for {sleep_time / 60} mins. before starting the next persona for the dataset")
                time.sleep(sleep_time)
        
        print(f"Sleeping for {sleep_time / 60} mins. before starting the next dataset")
        time.sleep(sleep_time)
