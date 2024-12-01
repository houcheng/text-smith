class Config:
    def __init__(self, config_data):
        self.config_data = config_data

    def get_action_prompts(self, action):
        return self.config_data.get(action, [])
class ActionConfig:
    def __init__(self, prompts, source=None, cache=False, model="openai/gpt-3.5-turbo"):
        self.prompts = prompts
        self.source = source
        self.cache = cache
        self.model = model

    def get_prompts(self, config):
        if self.prompts:
            return self.prompts
        elif self.source:
            source_action = config.get(self.source)
            if source_action:
                return source_action.get_prompts(config)
        return []

    def get_model(self):
        return self.model

    def get_cache(self):
        return self.cache

class Config:
    def __init__(self, config_data):
        self.config_data = {action: ActionConfig(data.get('prompts'), data.get('source'), data.get('cache', False), data.get('model', "openai/gpt-3.5-turbo")) for action, data in config_data.items()}

    def get_action_prompts(self, action):
        action_config = self.config_data.get(action)
        if action_config:
            return action_config.get_prompts(self.config_data)
        return []

    def get_action_model(self, action):
        action_config = self.config_data.get(action)
        if action_config:
            return action_config.get_model()
        return "openai/gpt-3.5-turbo"

    def get_action_cache(self, action):
        action_config = self.config_data.get(action)
        if action_config:
            return action_config.get_cache()
        return False

    def get_actions(self):
        return list(self.config_data.keys())

class Config:
    def __init__(self, config_data):
        self.config_data = {action: ActionConfig(data.get('prompts'), data.get('source')) for action, data in config_data.items()}

    def get_action_prompts(self, action):
        action_config = self.config_data.get(action)
        if action_config:
            return action_config.get_prompts(self.config_data)
        return []

    def get_actions(self):
        return list(self.config_data.keys())
