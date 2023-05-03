import json

def load_config():
    with open('config.json') as f:
        config = json.load(f)
    return config

def save_recent_app_user(config, recent_user):
    config['recent_app_user'] = recent_user
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)

def get_app_user(config):
    recent_app_user = config.get('recent_app_user', '')
    user_input = input(f"Please enter a user (press enter to use recent user: {recent_app_user}): ")

    if not user_input:
        user_input = recent_app_user

    save_recent_app_user(config, user_input)

    return user_input
