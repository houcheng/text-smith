import os
import requests

import os

from config import ActionConfig


def call_openrouter_api(file_content: str, user_prompts: str, model: str, cache: bool):
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": os.getenv('YOUR_SITE_URL', ''),  # Optional, for including your app on openrouter.ai rankings.
        "X-Title": os.getenv('YOUR_SITE_NAME', ''),  # Optional. Shows in rankings on openrouter.ai.
        "Content-Type": "application/json"
    }
    messages = [{"role": "system", "content": [{"type": "text", "text": prompt}]} for prompt in user_prompts]
    user_message = [{"type": "text", "text": file_content}]
    if cache:
        user_message[0]['cache_control'] = {"type": "ephemeral"}
    messages.append({"role": "user", "content": user_message})
    body = {
        "model": model,
        "messages": messages
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()['choices'][0]['message']['content']

def process_file(action, file_path, action_config: ActionConfig):
    with open(file_path, 'r') as file:
        file_content = file.read()

    system_prompts = action_config.get_prompts()
    output_text = call_openrouter_api(file_content, system_prompts, action_config.model, action_config.cache)

    base_name, ext = os.path.splitext(file_path)
    output_file_path = f"{base_name}[{action}].{ext}"
    with open(output_file_path, 'w') as output_file:
        output_file.write(output_text)

    print(f"Output written to {output_file_path}")
