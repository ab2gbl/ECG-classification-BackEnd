from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import torch
from .detection_model import UNet1D_Enhanced
import numpy as np
import json
import os
import asyncio
class SegmentationAgent(Agent):
    class ReceiveAndSegment(CyclicBehaviour):
        async def run(self):
            print("Waiting for message...")
            msg = await self.receive(timeout=10)  # Wait up to 10 seconds
            if msg:
                print("Got message ✅")
                print("[SegmentationAgent] Received ECG")
                
                signal = np.array(json.loads(msg.body))  # ✅ Parse safely
                #signal = np.array(eval(msg.body))  # Safely parse string to numpy array
                signal = signal.reshape(1, 1, -1)  # (1, 1, L)
                window_size = 240
                segments = []
                
                for i in range(0, signal.shape[2] - window_size + 1, window_size):
                    window = signal[:, :, i:i+window_size]
                    segments.append(window)
                # Simulate segmentation

                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

                # Initialize model


                model_path = os.path.join(os.path.dirname(__file__), "models", "unet1d_ecg_qrs.pth")
                model_deep = UNet1D_Enhanced(n_classes=4).to(device)
                model_deep.load_state_dict(torch.load(model_path, map_location=device))
                model_deep.to(device)
                model_deep.eval()
                try:

                    predictions = []
                    with torch.no_grad():
                        for window in segments:
                            window = torch.tensor(window, dtype=torch.float32).to(device)
                            output = model_deep(window)  # (1, C, L)
                            pred = torch.argmax(output, dim=1).cpu().numpy()[0]  # (L,)
                            predictions.append(pred)

                    full_prediction = np.concatenate(predictions)
                    print("predected: ",predictions[-2])
                    out_msg = Message(to="feature@localhost")
                    out_msg.body = str(full_prediction)

                    await asyncio.sleep(2)
                    await self.send(out_msg)

                except Exception as e:
                    print("message", str(e))
                                
                # ✅ Unmount the model to save memory
                del model_deep
                torch.cuda.empty_cache()
                print("[SegmentationAgent] Model unloaded.")
            else:
                print("No message received ❌")

    async def setup(self):
        print(f"[{self.jid}] SegmentationAgent started.")
        self.add_behaviour(self.ReceiveAndSegment())
