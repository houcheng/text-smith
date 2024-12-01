model_map = {
    "qq": "qwen/qwen-2.5-coder-32b-instruct",
    "qq72": "qwen/qwen-2.5-72b-instruct",
    "ss": "anthropic/claude-3.5-sonnet",
    "qwq": "qwen/qwq-32b-preview"
}

class ActionConfig:
    def __init__(self, prompts, source, cache, model):
        if not prompts:
            raise ValueError("prompts can not be empty")
        self.prompts = prompts
        self.source = source
        self.cache = cache
        self.model = model

    def get_prompts(self, config):
        if self.prompts:
            return '\n'.join(self.prompts)
        elif self.source:
            source_action = config.get(self.source)
            if source_action:
                return source_action.get_prompts(config)
        return ''

    def get_model(self):
        return self.model

    def get_cache(self):
        return self.cache

class Config:
    def __init__(self, config_data):
        self.actions = {}
        print(config_data)
        for key in config_data.keys():
            self.actions[key] = \
                ActionConfig(config_data[key].get('prompts', ''),
                             config_data[key].get('source', ''),
                             config_data[key].get('cache', False),
                             config_data[key].get('model', "openai/gpt-3.5-turbo"))
        self.config_data = {action: ActionConfig(data.get('prompts'), data.get('source'), data.get('cache', False), data.get('model', "openai/gpt-3.5-turbo")) for action, data in config_data.items()}

