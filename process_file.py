import os
import requests

import os

from config import ActionConfig


def call_openrouter_api(file_content: str, user_prompts: str, model: str, cache: bool):
    # Environment variables used:
    # - OPENROUTER_API_KEY: Required for API authentication
    # - YOUR_SITE_URL: Optional, for including your app on openrouter.ai rankings
    # - YOUR_SITE_NAME: Optional, for including your app on openrouter.ai rankings

    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    your_site_url = os.getenv('YOUR_SITE_URL')
    your_site_name = os.getenv('YOUR_SITE_NAME')
    if your_site_url:
        headers["HTTP-Referer"] = your_site_url  # Optional, for including your app on openrouter.ai rankings.
    if your_site_name:
        headers["X-Title"] = your_site_name  # Optional. Shows in rankings on openrouter.ai.
    messages = [
        {"role": "system", "content": [{"type": "text", "text": "Given the attached text below:"}]},
        {"role": "user", "content": [{"type": "text", "text": file_content}]}
    ]
    if cache:
        messages[1]["content"][0]['cache_control'] = {"type": "ephemeral"}
    if user_prompts:
        messages.append({"role": "user", "content": [{"type": "text", "text": "\n".join(user_prompts)}]})
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
