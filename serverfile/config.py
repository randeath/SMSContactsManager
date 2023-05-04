import json
import os

def load_config():
    config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_file_path) as f:
        config = json.load(f)
    return config

def save_recent_user(user, config_data):
    config_data['recent_app_user'] = user
    config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_file_path, 'w') as f:
        json.dump(config_data, f, indent=4)

def get_app_user(config):
    recent_app_user = config.get('recent_app_user', '')
    return recent_app_user
