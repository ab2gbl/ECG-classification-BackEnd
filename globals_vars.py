import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

config = load_config()

def get_TCN():
    return config['TCN_model_run_id']
def set_TCN(value):
    config['TCN_model_run_id'] = value
    save_config(config)

def get_UNet():
    return config['UNet_model_run_id']
def set_UNet(value):
    config['UNet_model_run_id'] = value
    save_config(config)
