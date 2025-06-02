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
# TCN model 
def get_TCN():
    return config['TCN_model_run_id']
def set_TCN(value):
    config['TCN_model_run_id'] = value
    save_config(config)
# UNet model
def get_UNet():
    return config['UNet_model_run_id']
def set_UNet(value):
    config['UNet_model_run_id'] = value
    save_config(config)
# R detection model
def get_R_detection():
    return config['R_detection_model_run_id']
def set_R_detection(value):
    config['R_detection_model_run_id'] = value
    save_config(config)
# Beat classification model
def get_beat_classification():
    return config['Beat_model_run_id']
def set_beat_classification(value):
    config['Beat_model_run_id'] = value
    save_config(config)
# Signal normality model
def get_signal_normality_model():
    return config['Signal_normality_model_run_id']
def set_signal_normality_model(value):
    config['Signal_normality_model_run_id'] = value
    save_config(config)
# Signal SB model
def get_signal_SB_model():
    return config['Signal_SB_model_run_id']
def set_signal_SB_model(value):
    config['Signal_SB_model_run_id'] = value
    save_config(config)