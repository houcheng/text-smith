import os
import yaml
import glob
# import openrouter

from config import Config, model_map

def get_action_from_path(file_path):
    """Extract the action from the file path."""
    base_name = os.path.splitext(file_path)[0]
    parts = base_name.split('[')
    if len(parts) > 1:
        action = parts[-1].split(']')[0]
        return action
    return None


def load_config(config_path):
    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)
        print(config_data)
        return Config(config_data)

def get_config_path():
    if os.path.exists('.ts.conf.yml'):
        return '.ts.conf.yml'
    home_dir = os.path.expanduser('~')
    if os.path.exists(os.path.join(home_dir, '.ts.conf.yml')):
        return os.path.join(home_dir, '.ts.conf.yml')
    return None

import requests

def call_openrouter_api(action, file_content, system_prompts, model="openai/gpt-3.5-turbo"):
    api_key = 'your_api_key_here'
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "YOUR_SITE_URL",  # Optional, for including your app on openrouter.ai rankings.
        "X-Title": "YOUR_SITE_NAME",  # Optional. Shows in rankings on openrouter.ai.
        "Content-Type": "application/json"
    }
    messages = [{"role": "system", "content": prompt} for prompt in system_prompts]
    messages.append({"role": "user", "content": file_content})
    body = {
        "model": model,
        "messages": messages
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()['choices'][0]['message']['content']

def process_init_command():
    print("Initializing configuration...")
    # Add initialization logic here

def process_file(action, file_path, config, model):
    with open(file_path, 'r') as file:
        file_content = file.read()

    action_config = config.actions.get(action)
    if not action_config:
        raise ValueError(f"Action '{action}' not found in config")

    system_prompts = action_config.get_prompts(config)
    output_text = call_openrouter_api(action, file_content, system_prompts, model)

    base_name, ext = os.path.splitext(file_path)
    output_file_path = f"{base_name}-{action}{ext}"
    with open(output_file_path, 'w') as output_file:
        output_file.write(output_text)

    print(f"Output written to {output_file_path}")


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Process files with Openrouter API")
    parser.add_argument("command", help="The command to perform (e.g., write, init)")
    parser.add_argument("action", help="The action to perform (e.g., fix, note, summary, all)", nargs='?')
    parser.add_argument("file_paths", help="The path(s) to the file(s) to process", nargs='+')
    parser.add_argument("--model", choices=model_map.keys(), default="qq", help="The model to use (qq: qwen32, qq72: qwen72, ss: sonet3.5)")

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
    config = load_config(config_path)

    if args.action and args.action not in config.actions and args.action != "all":
        print(f"Unknown action '{args.action}'.")
        sys.exit(1)

    command = args.command
    action = args.action
    file_paths = args.file_paths
    model = model_map[args.model]
    print("file_paths", file_paths)
    if not action or not file_paths:
        print("Action and file_paths are required for the write command.")
        sys.exit(1)

    expanded_file_paths = []
    for file_pattern in file_paths:
        expanded_file_paths.extend([f for f in glob.glob(file_pattern) if get_action_from_path(f) is None])

    if not expanded_file_paths:
        print("No files found matching the provided patterns.")
        sys.exit(1)

    for file_path in expanded_file_paths:
        if action == "all":
            for config_action in config.actions:
                process_file(config_action, file_path, config, model)
        else:
            process_file(action, file_path, config, model)

if __name__ == "__main__":
    main()
