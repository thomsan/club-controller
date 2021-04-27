import copy
import json
import os
from threading import Lock


class ConfigManager():
    def __init__(self, config_file_path, default_config=None):
        self.config_file_path = config_file_path
        self.file_lock = Lock()
        if default_config == None:
            default_config = {}
        self.config = copy.deepcopy(default_config)

        if not os.path.exists(self.config_file_path):
            self.save()

        with open(self.config_file_path) as json_file:
            self.config = json.load(json_file)


    def get(self):
        return self.config


    def update(self, new_config):
        for key, value in new_config.items():
            self.config[key] = value


    def save(self):
        with open(self.config_file_path, "w") as f:
            json.dump(self.config, f, indent=4)
