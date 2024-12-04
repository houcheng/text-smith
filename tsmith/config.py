model_map = {
    "qq": "qwen/qwen-2.5-coder-32b-instruct",
    "qq72": "qwen/qwen-2.5-72b-instruct",
    "ss": "anthropic/claude-3.5-sonnet",
    "qwq": "qwen/qwq-32b-preview",
    "ff": "google/gemini-flash-1.5"
    # "ff": "openrouter/google/gemini-flash-1.5-exp"
}

from chunk_cutter import ChunkCutter, TimestampChunkCutter

class ActionConfig:
    def __init__(self, prompts, source, cache, model, cutter: ChunkCutter | None = None):
        if not prompts:
            raise ValueError("prompts can not be empty")
        self.prompts = prompts
        self.source = source
        self.cache = cache
        self.model = model
        self.cutter = cutter

    def get_prompts(self):
        return self.prompts

    def get_model(self):
        return self.model

    def get_cache(self):
        return self.cache

    def get_cutter(self):
        return self.cutter

class Config:
    def __init__(self, config_data, model: str, file_path: str | None = None):
        self.actions = {}
        print(config_data)
        for key in config_data.keys():
            timestamp_chunk_size = config_data[key].get('timestamp_chunk_size')
            if timestamp_chunk_size:
                cutter = TimestampChunkCutter(chunk_size=timestamp_chunk_size)
            else:
                cutter = None

            self.actions[key] = \
                ActionConfig(config_data[key].get('prompts', ''),
                             config_data[key].get('source', ''),
                             config_data[key].get('cache', False),
                             model,
                             cutter)
        self.config_data = self.actions

