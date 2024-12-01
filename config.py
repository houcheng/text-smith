class Config:
    def __init__(self, config_data):
        self.config_data = config_data

    def get_action_prompts(self, action):
        return self.config_data.get(action, [])
