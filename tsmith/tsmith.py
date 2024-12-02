import os
import yaml
import glob
# import openrouter

from config import Config, model_map
from process_file import process_file


def get_action_from_path(file_path):
    """Extract the action from the file path."""
    base_name = os.path.splitext(file_path)[0]
    parts = base_name.split('[')
    if len(parts) > 1:
        action = parts[-1].split(']')[0]
        return action
    return None


def load_config(config_path, model) -> Config:
    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)
        print(config_data)
        return Config(config_data, model)

def get_config_path() -> str | None:
    if os.path.exists('../.ts.conf.yml'):
        return '.ts.conf.yml'
    home_dir = os.path.expanduser('~')
    if os.path.exists(os.path.join(home_dir, '../.ts.conf.yml')):
        return os.path.join(home_dir, '../.ts.conf.yml')
    return None


def process_init_command() -> None:
    config_path = '../.ts.conf.yml'
    if os.path.exists(config_path):
        print(f"Warning: Configuration file '{config_path}' already exists in the current directory.")
    else:
        default_config = """fix:
    prompts:
        - "The attached text is transaction text by AI."
        - "Fix error and modify if sentence does not make sense."
        - "Fix hallucination and make the sentence more readable."
        - "Make the article more readable and separate into paragraphs."
        - "Do not changes too much"
        - "Must write in its origin language"
note:
    source: fix
    prompts:
        - "Write note for the attached text in its origin language."
    cache: true
summary:
    source: fix
    prompts:
        - "Write a summary for the attached text in its origin language."
    cache: true
"""
        with open(config_path, 'w') as file:
            file.write(default_config)
        print(f"Configuration file '{config_path}' created in the current directory.")


def main():
    print("tsmith command is running.")
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Process files with Openrouter API\nDefault config is .ts.conf.yml in home or current directory")
    parser.add_argument("command", help="The command to perform (e.g., write, init)")
    parser.add_argument("action", help="The action to perform (e.g., fix, note, summary, all)", nargs='?')
    parser.add_argument("file_paths", help="The path(s) to the file(s) to process", nargs='*')
    parser.add_argument("--model", choices=model_map.keys(), default="qq", help="The model to use (qq: qwen32, qq72: qwen72, ss: sonnet3.5)")

    args = parser.parse_args()

    if args.command == "init":
        process_init_command()
        sys.exit(0)
    elif args.command != "write":
        print(f"Unknown command '{args.command}'.")
        sys.exit(1)

    # write command
    config_path = get_config_path()
    if not config_path:
        raise FileNotFoundError("Configuration file not found")
    config = load_config(config_path, model_map[args.model])

    if args.action and args.action not in config.actions and args.action != "all":
        print(f"Unknown action '{args.action}'.")
        sys.exit(1)

    file_paths = args.file_paths
    action = args.action
    if not action or not file_paths:
        print("Action and file_paths are required for the write command.")
        sys.exit(1)

    print("file_paths", file_paths)
    expanded_file_paths = []
    for file_pattern in file_paths:
        expanded_file_paths.extend([f for f in glob.glob(file_pattern) if get_action_from_path(f) is None])

    if not expanded_file_paths:
        print("No files found matching the provided patterns.")
        sys.exit(1)

    for file_path in expanded_file_paths:
        if action == "all":
            # Process actions with no source first
            for config_action in [act for act in config.actions if not config.actions[act].source]:
                process_file(config_action, file_path, config.actions[config_action])
            # Process actions with a source next
            for config_action in [act for act in config.actions if config.actions[act].source]:
                process_file(config_action, file_path, config.actions[config_action])
        else:
            process_file(action, file_path, config.actions[action])

if __name__ == "__main__":
    main()
