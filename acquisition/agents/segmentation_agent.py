from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import torch
from .segmentation_model import UNet1D_Enhanced
import numpy as np
import json
import os
import asyncio

from scipy.ndimage import median_filter, label
from tensorflow.keras.utils import register_keras_serializable
from keras.saving import load_model
import tensorflow as tf
from tensorflow.keras import backend as K
import gc

from tqdm import tqdm

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

def post_process_predictions(predictions, threshold=0.5, min_duration=20):
    """
    Apply post-processing to all predicted segments.

    predictions: np.array of shape (num_segments, segment_length, 3)
    threshold: float, classification threshold
    min_duration: int, minimum valid blob length in samples
    """
    num_segments, segment_len, num_classes = predictions.shape
    cleaned = np.zeros_like(predictions)

    for seg in range(num_segments):
        for cls in range(num_classes):
            # Threshold
            binary_mask = predictions[seg, :, cls] > threshold

            # Median filter to remove flickers
            smoothed = median_filter(binary_mask.astype(int), size=7)

            # Remove short blobs
            labeled_array, num_features = label(smoothed)
            for i in range(1, num_features + 1):
                blob = (labeled_array == i)
                if blob.sum() >= min_duration:
                    cleaned[seg, :, cls][blob] = 1
    return cleaned

class SegmentationAgent(Agent):
    class ReceiveAndSegment(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)  # Wait up to 10 seconds
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
                    
                    for i in range(0, signal.shape[2] - window_size + 1, window_size)   :
                        window = signal[:, :, i:i+window_size]
                        segments.append(window)
                    # Simulate segmentation

                    device = torch.device("cuda" if torch.cuda.is_available(    ) else "cpu")

                    # Initialize model


                    model_path = os.path.join(os.path.dirname(__file__), "models", "unet1d_ecg_qrs.pth")
                    model_deep = UNet1D_Enhanced(n_classes=4).to(device)
                    model_deep.load_state_dict(torch.load(model_path, map_location=device))
                    model_deep.to(device)
                    model_deep.eval()
                    try:

                        predictions = []
                        print("Starting predection")
                        i=0
                        with torch.no_grad():
                            for i in tqdm(range(len(segments)), desc="detection"):
                                window = segments[i]
                                
                                window = torch.tensor(window, dtype=torch.float32).to(device)
                                output = model_deep(window)  # (1, C, L)
                                pred = torch.argmax(output, dim=1).cpu().numpy()[0]  # (L,)
                                predictions.append(pred)
                                

                        full_prediction = np.concatenate(predictions).tolist() 

                        # ✅ Unmount the model to save memory
                        del model_deep
                        torch.cuda.empty_cache()
                        print("[SegmentationAgent] Model unloaded.")
                    except Exception as e:
                        print("message", str(e))
                        #print("predected: ",predictions[-2])
                elif model=="TCN":
                    window_size = 250  # 1-second window
                    new_segments = segment_signal(signal, window_size , 250)
                    new_segments = new_segments.reshape(-1, window_size, 1)

                    
                    model_path = os.path.join(os.path.dirname(__file__), "models", "first_QRS_T_P.keras")
                    model = load_model(model_path, custom_objects={
                        'weighted_binary_crossentropy': weighted_binary_crossentropy
                    })

                    # Predict QRS regions
                    y_pred = model.predict(new_segments)
                    
                    y_pred = (y_pred > 0.5).astype(int)  # Convert probabilities to binary masks
                    #print(y_pred[y_pred > 0])  # P
                    y_pred_clean = post_process_predictions(y_pred, threshold=0.5, min_duration=int(0.03 * 250))
                    
                    full_prediction = []

                                        
                    for window in y_pred:
                        for vec in window:  # vec is shape (3,)
                            if np.all(vec == 0):
                                full_prediction.append(0)  # background
                            else:
                                full_prediction.append(np.argmax(vec) + 1)  # class 1–3# flatten manually
                    
                    full_prediction = [int(x) for x in full_prediction]



                    del model
                    K.clear_session()
                    gc.collect()


                    # Send result back to controller
                response = Message(to="controller@localhost")
                response.body = json.dumps({
                    "full_prediction": full_prediction # Your processed signal
                })
                await self.send(response)
                print("[SegmentationAgent] ✅ Sent detection back to controller")
                                
                

    async def setup(self):
        print(f"[{self.jid}] SegmentationAgent started.")
        self.add_behaviour(self.ReceiveAndSegment())
