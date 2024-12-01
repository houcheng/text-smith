import os
import requests

import os

from config import ActionConfig


def call_openrouter_api(file_content: str, user_prompts: str, model: str, cache: bool) -> str:
    # Environment variables used:
    # - OPENROUTER_API_KEY: Required for API authentication
    # - YOUR_SITE_URL: Optional, for including your app on openrouter.ai rankings
    # - YOUR_SITE_NAME: Optional, for including your app on openrouter.ai rankings
    # Returns the output text from the API

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

    # https://openrouter.ai/docs/prompt-caching
    messages = [
        # 0
        { "role": "system",
          "content": [
              {"type": "text", "text": "Given the attached text below:"},
              {"type": "text", "text": file_content},
              {"type": "text", "text": "You should reply with ========== as first line then no personal comment just output the processed text."}
          ]
        },
        # 1
        {"role": "user", "content": [{"type": "text", "text": user_prompts}]}
    ]
    if cache:
        messages[1]["content"][1]['cache_control'] = {"type": "ephemeral"}
    body = {
        "model": model,
        "messages": messages
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
    response.raise_for_status()  # Raise an error for bad responses
    # print(response.json())
    response_content = response.json()['choices'][0]['message']['content']
    lines = response_content.split('\n')
    if lines[0] == '=':
        response_content = '\n'.join(lines[1:])
    else:
        print("Warning: Format not aligned. The response does not start with '='.")
    print(response_content)
    return response_content

def process_file(action, file_path, action_config: ActionConfig):
    with open(file_path, 'r') as file:
        file_content = file.read()

    system_prompts = action_config.get_prompts()
    output_text = call_openrouter_api(file_content, system_prompts, action_config.model, action_config.cache)

    base_name, ext = os.path.splitext(file_path)
    output_file_path = f"{base_name}[{action}]{ext}"
    with open(output_file_path, 'w') as output_file:
        output_file.write(output_text)

    print(f"Output written to {output_file_path}")
