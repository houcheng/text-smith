import os
import requests

from config import ActionConfig

def get_system_prompts():
    system_prompts_path = os.path.join(os.path.dirname(__file__), 'system_prompts.txt')
    with open(system_prompts_path, 'r', encoding='utf-8') as file:
        return file.read()

def call_openrouter_api(file_content: str, user_prompts: str, model: str, cache: bool) -> str:
    # Environment variables used:
    # - OPENROUTER_API_KEY: Required for API authentication
    # - YOUR_SITE_URL: Optional, for including your app on openrouter.ai rankings
    # - YOUR_SITE_NAME: Optional, for including your app on openrouter.ai rankings
    # Returns the output text from the API
    print(f"Calling OpenRouter API {len(file_content)} bytes, model: {model}, cache: {cache}")
    # print(f"Content: ", file_content)
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    your_site_url = os.getenv('www.github.com/houcheng/text-smith')
    your_site_name = 'text-smith'
    if your_site_url:
        headers["HTTP-Referer"] = your_site_url  # Optional, for including your app on openrouter.ai rankings.
    if your_site_name:
        headers["X-Title"] = your_site_name  # Optional. Shows in rankings on openrouter.ai.

    system_prompts = get_system_prompts()
    # https://openrouter.ai/docs/prompt-caching
    messages = [
        # 0
        { "role": "system",
          "content": [
              {"type": "text", "text": "Given the attached text below:"},
              {"type": "text", "text": file_content},
              {"type": "text", "text": system_prompts} ]
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
    response_content = None
    try:
        response_content = response.json()['choices'][0]['message']['content']
    except:
        print("Error the response is: ", response.json())
    
    if not response_content:
        print("Error the response is: ", response.json())
        raise ValueError("Response content is empty")

    lines = response_content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('====='):
            response_content = '\n'.join(lines[i+1:])
            break
    else:
        print("Warning: Format not aligned. The response does not start with '====='.")
        # print("Response content:", response_content)
    return response_content

class ChunkCutter:
    def load(self, file_path):
        pass

    def get_chunk(self):
        yield ""

class TimestampChunkCutter(ChunkCutter):
    def __init__(self, chunk_size):
        self.chunk_size = chunk_size
        self.timestamps = []

    def load(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                if line.strip().startswith("*") or line.strip().startswith("0"):
                    if len(line.strip()) >= 8 and line.strip()[0:2].isdigit() and line.strip()[2] == ":" and line.strip()[3:5].isdigit() and line.strip()[5] == ":" and line.strip()[6:8].isdigit():
                        self.timestamps.append(line)

    def get_chunk(self):
        i = 0
        while i < len(self.timestamps):
            chunk_timestamps = []
            for _ in range(self.chunk_size):
                if i < len(self.timestamps):
                    chunk_timestamps.append(self.timestamps[i])
                    i += 1
                else:
                    break
            chunk_text = "".join(chunk_timestamps)
            yield chunk_text

def process_file(action, file_path, action_config: ActionConfig, rebuild: bool):
    # Update file_path from meeting-20241225.md to meeting-20241225@fix.md if action_config.source is fix
    if action_config.source:
        source_action = action_config.source
        source_base_name, source_ext = os.path.splitext(file_path)
        # Remove any existing action tag before appending the new one
        if '@' in source_base_name:
            source_base_name = source_base_name[:source_base_name.rfind('@')]
        source_output_file_path = f"{source_base_name}@{source_action}{source_ext}"
        if not os.path.exists(source_output_file_path):
            print(f"Source file '{source_output_file_path}' does not exist for action '{action}'. Skipping processing.")
            return
        file_path = source_output_file_path

    base_name, ext = os.path.splitext(file_path)
    # Remove any existing action tag before appending the new one
    if '@' in base_name:
        base_name = base_name[:base_name.rfind('@')]
    output_file_path = f"{base_name}@{action}{ext}"

    if not rebuild and os.path.exists(output_file_path) and os.path.getmtime(output_file_path) > os.path.getmtime(file_path):
        print(f"Output file '{output_file_path}' is newer than input file '{file_path}'. Skipping processing.")
        return

    system_prompts = action_config.get_prompts()
    cutter = action_config.get_cutter()

    output_text = ""
    with open(file_path, 'r', encoding='utf-8') as file:
        if cutter:
            cutter.load(file_path)
            # Process each chunk using the ChunkCutter's get_chunk method
            for chunk in cutter.get_chunk():
                output_text += call_openrouter_api(chunk, system_prompts, action_config.model, action_config.cache)
        else:
            file_content = file.read()
            output_text = call_openrouter_api(file_content, system_prompts, action_config.model, action_config.cache)

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(output_text)

    print(f"Output written to {output_file_path}")
