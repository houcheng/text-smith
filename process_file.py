import os
import requests

import os

def call_openrouter_api(action, file_content, system_prompts, model="openai/gpt-3.5-turbo"):
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")
    headers = {
        "Authorization": f"Bearer {api_key}",
        # "HTTP-Referer": "YOUR_SITE_URL",  # Optional, for including your app on openrouter.ai rankings.
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
