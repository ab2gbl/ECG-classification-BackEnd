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
# CNN-LSTM model
def get_CNN_LSTM():
    return config['CNN_LSTM_model_run_id']
def set_CNN_LSTM(value):
    config['CNN_LSTM_model_run_id'] = value
    save_config(config)
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
# Signal sinus_arrhythmia model
def get_signal_sinus_arrhythmia_model():
    return config['Signal_sinus_arrhythmia_model_run_id']
def set_signal_sinus_arrhythmia_model(value):
    config['Signal_sinus_arrhythmia_model_run_id'] = value
    save_config(config)
# Signal supraventricular_tachycardia model
def get_signal_supraventricular_tachycardia_model():
    return config['Signal_supraventricular_tachycardia_model_run_id']
def set_signal_supraventricular_tachycardia_model(value):
    config['Signal_supraventricular_tachycardia_model_run_id'] = value
    save_config(config)
# Signal sinus_tachycardia model
def get_signal_sinus_tachycardia_model():
    return config['Signal_sinus_tachycardia_model_run_id']
def set_signal_sinus_tachycardia_model(value):
    config['Signal_sinus_tachycardia_model_run_id'] = value
    save_config(config)

