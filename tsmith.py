import os
import yaml
# import openrouter

from config import Config

def load_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file)
            return Config(config_data)
    return None

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

def process_file(action, file_path, model=None):
    config_path = get_config_path()
    if not config_path:
        print("Configuration file not found.")
        return

    config = load_config(config_path)
    if not config:
        print("Configuration file not found.")
        return

    system_prompts = config.get_action_prompts(action)
    if not system_prompts:
        print(f"Action '{action}' not found in configuration.")
        return

    model_map = {
        "qq": "qwen/qwen-2.5-coder-32b-instruct",
        "qq72": "qwen/qwen-2.5-72b-instruct",
        "ss": "anthropic/claude-3.5-sonnet",
        "qwq": "qwen/qwq-32b-preview"
    }

    if model:
        model = model_map.get(model, model)
    else:
        model = config.get_action_model(action)
    cache = config.get_action_cache(action)

    with open(file_path, 'r') as file:
        file_content = file.read()

    output_text = call_openrouter_api(action, file_content, system_prompts, model)

    base_name, ext = os.path.splitext(file_path)
    output_file_path = f"{base_name}-{action}{ext}"
    with open(output_file_path, 'w') as output_file:
        output_file.write(output_text)

    print(f"Output written to {output_file_path}")

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Process files with Openrouter API")
    parser.add_argument("command", help="The command to perform (e.g., write, init)")
    parser.add_argument("action", help="The action to perform (e.g., fix, note, summary)")
    parser.add_argument("file_path", help="The path to the file to process")
    parser.add_argument("--model", choices=["qq", "qq72", "ss"], help="The model to use (qq: qwen32, qq72: qwen72, ss: sonet3.5)")

    args = parser.parse_args()

    command = args.command
    action = args.action
    file_path = args.file_path
    model = args.model

    if command == "write":
        process_file(action, file_path, model)
    elif command == "init":
        print("Initializing configuration...")
    else:
        print(f"Unknown command '{command}'.")
