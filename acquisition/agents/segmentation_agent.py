from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import torch
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), './ml_flow'))
sys.path.append(parent_dir)
import numpy as np
import json
from tensorflow.keras.utils import register_keras_serializable
import tensorflow as tf
import mlflow
from tqdm import tqdm
import globals_vars 


mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

@register_keras_serializable()
def weighted_binary_crossentropy(y_true, y_pred):
    weight = tf.reduce_mean(y_true) * 0.5 + 0.5
    loss = tf.keras.losses.binary_crossentropy(y_true, y_pred)
    return tf.reduce_mean(loss * weight)

def create_multi_class_mask(length, wave_regions):
    mask = np.zeros((length, 3))  # [P, QRS, T]
    label_map = {'p': 0, 'N': 1, 't': 2}
    for label, regions in wave_regions.items():
        for start, end in regions:
            mask[start:end, label_map[label]] = 1
    return mask

def segment_signal_and_mask(signal, mask, window_size, fs):
    segments = []
    masks = []
    for i in range(0, len(signal) - window_size, window_size // 5):  # 2% overlap
        segment = signal[i:i + window_size]
        mask_segment = mask[i:i + window_size]
        segments.append(segment)
        masks.append(mask_segment)
    return np.array(segments), np.array(masks)

def segment_signal(signal, window_size, fs):
    segments = []
    for i in range(0, len(signal) - window_size, window_size ):  # 50% overlap
        segment = signal[i:i + window_size]
        segments.append(segment)
    return np.array(segments)

class SegmentationAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.UNet_model = None
        self.UNet_run_id =  globals_vars.get_UNet()  
        self.TCN_model = None
        self.TCN_run_id = globals_vars.get_TCN()

    async def setup(self):
        print(f"[{self.jid}] SegmentationAgent started.")
        # Load the model during setup
        try:
            self.UNet_model = mlflow.pytorch.load_model(f"runs:/{self.UNet_run_id}/model").to(device)
            self.UNet_model.eval()
            print("[SegmentationAgent] UNet Model loaded successfully ✅")
            self.TCN_model = mlflow.keras.load_model(f"runs:/{self.TCN_run_id}/model", custom_objects={
                'weighted_binary_crossentropy': weighted_binary_crossentropy
            })
            print("[SegmentationAgent] TCN Model loaded successfully ✅")

        except Exception as e:
            print(f"[SegmentationAgent] Error loading model: {str(e)}")
            raise

        self.add_behaviour(self.ReceiveAndSegment())

    class ReceiveAndSegment(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)  # Wait up to 10 seconds
            if msg:
                print("[SegmentationAgent] Received ECG ✅")
                data = json.loads(msg.body)
                signal = np.array(data["signal"]) 
                if data["model"] =="TCN":
                    model = "TCN"
                else:
                    model = "UNet"
                if model=="UNet":
                    signal = signal.reshape(1, 1, -1)  # (1, 1, L)
                    window_size = 240
                    segments = []
                    
                    for i in range(0, signal.shape[2] - window_size + 1, window_size):
                        window = signal[:, :, i:i+window_size]
                        segments.append(window)

                    try:
                        predictions = []
                        print("Starting prediction")
                        with torch.no_grad():
                            for i in tqdm(range(len(segments)), desc="detection"):
                                window = segments[i]
                                window = torch.tensor(window, dtype=torch.float32).to(device)
                                output = self.agent.UNet_model(window)  # Use the agent's model instance
                                pred = torch.argmax(output, dim=1).cpu().numpy()[0]  # (L,)
                                predictions.append(pred)

                        full_prediction = np.concatenate(predictions).tolist() 
                        print("[SegmentationAgent] Prediction completed ✅")

                    except Exception as e:
                        print(f"[SegmentationAgent] Error during prediction: {str(e)}")
                        raise

                elif model=="TCN":
                    window_size = 250  # 1-second window
                    new_segments = segment_signal(signal, window_size , 250)
                    new_segments = new_segments.reshape(-1, window_size, 1)

                    
                    

                    # Predict QRS regions
                    y_pred = self.agent.TCN_model.predict(new_segments)
                    
                    y_pred = (y_pred > 0.5).astype(int)  # Convert probabilities to binary masks
                    #print(y_pred[y_pred > 0])  # P
                    #y_pred_clean = post_process_predictions(y_pred, threshold=0.5, min_duration=int(0.03 * 250))
                    
                    full_prediction = []

                                        
                    for window in y_pred:
                        for vec in window:  # vec is shape (3,)
                            if np.all(vec == 0):
                                full_prediction.append(0)  # background
                            else:
                                full_prediction.append(np.argmax(vec) + 1)  # class 1–3# flatten manually
                    
                    full_prediction = [int(x) for x in full_prediction]





                    # Send result back to controller
                response = Message(to="controller@localhost")
                response.body = json.dumps({
                    "full_prediction": full_prediction # Your processed signal
                })
                await self.send(response)
                print("[SegmentationAgent] ✅ Sent detection back to controller")
                                
                
