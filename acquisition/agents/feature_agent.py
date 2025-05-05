from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from .feature_functions import *
import asyncio
import numpy as np
import json
def convert_numpy(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(x) for x in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    else:
        return obj

class FeatureAgent(Agent):
    class ExtractFeatures(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                print("[FeatureAgent] Got segmentation")
                # Extract features
                data = json.loads(msg.body)
                signal = np.array(data["signal"]) 
                pred_labels = np.array(data["mask"]) 
                
                print(f"[FeatureAgent] Got signal {signal.shape} and mask {pred_labels.shape}")
                features_per_beat = extract_features_per_qrs(signal, pred_labels)
                print(f"[FeatureAgent] Extracted features: {len(features_per_beat)}")
                # Convert numpy arrays to lists for JSON serialization
                features_per_beat = convert_numpy(features_per_beat)

                response = Message(to="controller@localhost")
                response.body = json.dumps({
                    "features": features_per_beat # Your processed signal
                })
                await self.send(response)
                print("[FeatureAgent] ✅ Sent processed ECG back to controller")

    async def setup(self):
        print(f"[{self.jid}] FeatureAgent started.")
        self.add_behaviour(self.ExtractFeatures())
