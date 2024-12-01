import os
import yaml
import openrouter

def load_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    return {}

def get_config_path():
    if os.path.exists('.ts.conf.yml'):
        return '.ts.conf.yml'
    home_dir = os.path.expanduser('~')
    if os.path.exists(os.path.join(home_dir, '.ts.conf.yml')):
        return os.path.join(home_dir, '.ts.conf.yml')
    return None

def call_openrouter_api(action, file_content, system_prompts):
    client = openrouter.Client(api_key='your_api_key_here')
    messages = [{"role": "system", "content": prompt} for prompt in system_prompts]
    messages.append({"role": "user", "content": file_content})
    response = client.chat(messages)
    return response['choices'][0]['message']['content']

def process_file(action, file_path):
    config_path = get_config_path()
    if not config_path:
        print("Configuration file not found.")
        return

    config = load_config(config_path)
    if action not in config:
        print(f"Action '{action}' not found in configuration.")
        return

    with open(file_path, 'r') as file:
        file_content = file.read()

    system_prompts = config[action]
    output_text = call_openrouter_api(action, file_content, system_prompts)

    base_name, ext = os.path.splitext(file_path)
    output_file_path = f"{base_name}-{action}{ext}"
    with open(output_file_path, 'w') as output_file:
        output_file.write(output_text)

    print(f"Output written to {output_file_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: tsmith.py <action> <file_path>")
        sys.exit(1)

    action = sys.argv[1]
    file_path = sys.argv[2]
    process_file(action, file_path)
