import json

def load_config(file_path):
    with open(file_path) as f:
        config = json.load(f)
    return config

def update_config(file_path, config):
    with open(file_path, 'w') as f:
        json.dump(config, f)
