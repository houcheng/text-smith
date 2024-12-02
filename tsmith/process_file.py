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
              # {"type": "text", "text": "You should reply with ========== as first line and no need say `Let's start ` or similar extra words, just focus on the replying content."}
              {"type": "text", "text": """You should reply with ========== as first line and no need say `Let's start` or similar extra words, just focus on the replying content.
         IMPORTANT RULES:
         1. You MUST process and return the COMPLETE text
         2. NO summarization or content skipping allowed
         3. NO "[續原文內容省略]" or similar skip markers
         4. If any chinese characters are output, they must be in traditional chinese
         4. If content is too long, split into parts but process ALL of it
         5. Failure to process the complete text is considered task failure"""} ]
        },
        # 1
        {"role": "user", "content": [{"type": "text", "text": user_prompts}]}
    ]
    if cache:
        messages[0]["content"][1]['cache_control'] = {"type": "ephemeral"}
    body = {
        "model": model,
        "messages": messages
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
    response.raise_for_status()  # Raise an error for bad responses
    response_content = response.json()['choices'][0]['message']['content']
    if not response_content:
        print("Error the response is: ", response.json())
        raise ValueError("Response content is empty")

    lines = response_content.split('\n')
    if lines[0].startswith('====='):
        response_content = '\n'.join(lines[1:])
    else:
        print("Warning: Format not aligned. The response does not start with '====='.")
        print(response.json())
    # print(response_content)
    # may cause problem
    return response_content

import os.path

def process_file(action, file_path, action_config: ActionConfig):
    # Update file_path from meeting-20241225.md to meeting-meeting-20241225[fix].md if action_config.source is fix
    if action_config.source:
        source_action = action_config.source
        source_base_name, source_ext = os.path.splitext(file_path)
        source_output_file_path = f"{source_base_name}[{source_action}]{source_ext}"
        if not os.path.exists(source_output_file_path):
            print(f"Source file '{source_output_file_path}' does not exist for action '{action}'. Skipping processing.")
            return
        file_path = source_output_file_path

    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    base_name, ext = os.path.splitext(file_path)
    output_file_path = f"{base_name}[{action}]{ext}"

    if os.path.exists(output_file_path) and os.path.getmtime(output_file_path) > os.path.getmtime(file_path):
        print(f"Output file '{output_file_path}' is newer than input file '{file_path}'. Skipping processing.")
        return

    system_prompts = action_config.get_prompts()
    output_text = call_openrouter_api(file_content, system_prompts, action_config.model, action_config.cache)

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(output_text)

    print(f"Output written to {output_file_path}")
