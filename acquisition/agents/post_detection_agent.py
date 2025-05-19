from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
import numpy as np
import json
from .post_detection_functions import *

class PostDetectionAgent(Agent):
    class PostProcess(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                print("[PostDetectionAgent] Got segmentation:")
                data = json.loads(msg.body)
                signal = np.array(data["signal"]) 
                pred_labels = np.array(data["mask"]) 
                

                pred_labels = remove_uncomplete_first_last_wave(pred_labels)
                pred_labels = merge_close_waves(pred_labels)
                pred_labels = remove_irrelevant_waves(pred_labels)
                pred_labels = check_repeated_waves(pred_labels)


                pred_labels = fix_P(signal,pred_labels)
                pred_labels = fast_fix_QRS(signal,mask=pred_labels,fs=250)
                pred_labels = merge_close_waves(pred_labels)

                # Extract features
                features = "HR: 72 bpm, PR: 120ms"
                response = Message(to="controller@localhost")
                response.body = json.dumps({
                    "full_prediction": pred_labels.tolist() # Your processed signal
                })
                await self.send(response)
                print("[PostDetectionAgent] ✅ Sent processed ECG back to controller")
        

    async def setup(self):
        print(f"[{self.jid}] PostDetectionAgent started.")
        self.add_behaviour(self.PostProcess())
