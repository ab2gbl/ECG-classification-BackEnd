from .acquisition_agent import AcquisitionAgent
from .segmentation_agent import SegmentationAgent
from .feature_agent import FeatureAgent
from .decision_agent import DecisionAgent
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
import json
import asyncio
import base64
from asyncio import Event
class ControllerAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.final_result = []
        self.normalized_signal = None
        self.result_ready = Event()
    class PipelineManager(OneShotBehaviour):
        async def run(self):
            print("[ControllerAgent] Starting pipeline...")
            start_step = self.get("start_step") if self.get("start_step") is not None else 0
            end_step = self.get("end_step") if self.get("end_step") is not None else 4

            
            steps = range(start_step, end_step + 1)
            if 0 in steps:
                ecg_dat_file = self.get("ecg_dat")  # InMemoryUploadedFile
                ecg_hea_file = self.get("ecg_hea")  # InMemoryUploadedFile
                dat_bytes = ecg_dat_file.read()
                hea_bytes = ecg_hea_file.read()

                # Encode to base64 so you can send via text
                dat_b64 = base64.b64encode(dat_bytes).decode('utf-8')
                hea_b64 = base64.b64encode(hea_bytes).decode('utf-8')

                msg = Message(to="acquirer@localhost")
                msg.body = json.dumps({
                    "dat_file": dat_b64,
                    "hea_file": hea_b64
                })
                

                await self.send(msg)
                print("[ControllerAgent] 📨 Sent data to AcquisitionAgent")

                # Wait for response
                response = await self.receive(timeout=15)
                if response:
                    print("[ControllerAgent] ✅ Received response from AcquisitionAgent")
                else:
                    print("[ControllerAgent] ❌ No response from AcquisitionAgent")


                self.agent.final_result.append(response.body)
                if 1 not in steps:

                    print("[ControllerAgent] Final result got")
                    self.agent.result_ready.set()  
                else:
                    self.agent.normalized_signal = json.loads(response.body)["normalized_signal"]
                
            if 1 in steps:
                print("[ControllerAgent] Sending ECG data...")
                msg = Message(to="segmenter@localhost")
                msg.body = json.dumps({
                    "signal": self.agent.normalized_signal,
                    "model": self.get("model")
                })
                await self.send(msg)
                print("[ControllerAgent] 📨 Sent data to SegmentationAgent")

                # Wait for response
                response = await self.receive(timeout=15)
                if response:
                    print("[ControllerAgent] ✅ Received response from SegmentationAgent")
                else:
                    print("[ControllerAgent] ❌ No response from SegmentationAgent")


                self.agent.final_result.append(response.body)
                if 2 not in steps:
                    print("[ControllerAgent] Final result got")
                    self.agent.result_ready.set()  
              



            

    async def setup(self):
        print(f"[{self.jid}] ControllerAgent ready.")
        self.add_behaviour(self.PipelineManager())
