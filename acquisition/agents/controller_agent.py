from .acquisition_agent import AcquisitionAgent
from .segmentation_agent import SegmentationAgent
from .feature_agent import FeatureAgent
from .beat_classifier_agent import BeatClassifierAgent
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
import json
import asyncio
import base64
from asyncio import Event
from ..models import Signal, SignalFeatures
from asgiref.sync import sync_to_async

class ControllerAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.final_result = {}
        self.normalized_signal = None
        self.result_ready = Event()
        self.mask = None
        self.features = None
    def reset_result(self):
        self.final_result = {}
        self.normalized_signal = None
        self.result_ready.clear()
        self.result_ready = Event()
        self.mask = None
        self.features = None

    
    class PipelineManager(OneShotBehaviour):
        async def run(self):
            print("[ControllerAgent] Starting pipeline...")
            start_step = self.get("start_step") if self.get("start_step") is not None else 0
            end_step = self.get("end_step") if self.get("end_step") is not None else 5

            
            steps = range(start_step, end_step + 1)
            print(f"[ControllerAgent] Start and End: {start_step} - {end_step}")
            if 0 in steps:
                ecg_dat_file = self.get("ecg_dat")  # InMemoryUploadedFile
                ecg_hea_file = self.get("ecg_hea")  # InMemoryUploadedFile
                ecg_signal_start = self.get("signal_start") if self.get("signal_start") is not None else 0
                ecg_signal_end = self.get("signal_end") if self.get("signal_end") is not None else None
                dat_bytes = ecg_dat_file.read()
                hea_bytes = ecg_hea_file.read()

                # Encode to base64 so you can send via text
                dat_b64 = base64.b64encode(dat_bytes).decode('utf-8')
                hea_b64 = base64.b64encode(hea_bytes).decode('utf-8')

                msg = Message(to="acquirer@localhost")
                msg.body = json.dumps({
                    "dat_file": dat_b64,
                    "hea_file": hea_b64,
                    "signal_start": ecg_signal_start,
                    "signal_end": ecg_signal_end
                })
                

                await self.send(msg)
                print("[ControllerAgent] 📨 Sent data to AcquisitionAgent")
                print(f"[ControllerAgent] JID: {self.agent.jid}")
                # Wait for response
                print("[ControllerAgent] Waiting for response from AcquisitionAgent...")
                
                response = None
                timeout = 10  # seconds
                interval = 0.5  # polling interval
                elapsed = 0

                while elapsed < timeout:
                    response = await self.receive(timeout=interval)
                    if response:
                        break
                    elapsed += interval
                if response:
                    print("[ControllerAgent] ✅ Received response from AcquisitionAgent")
                else:
                    
                    print("[ControllerAgent] ❌ No response from AcquisitionAgent")
                    self.agent.result_ready.set()  
                    return 


                self.agent.final_result.update(json.loads(response.body))
                if 1 not in steps:

                    print("[ControllerAgent] Final result got")
                    self.agent.result_ready.set()  
                else:
                    self.agent.normalized_signal = json.loads(response.body)["normalized_signal"]
                
            
              
            if 1 in steps:
                if 0 not in steps:
                    self.agent.normalized_signal = self.get("normalized_signal")
                    self.agent.final_result.update({"normalized_signal": self.agent.normalized_signal})
                    
                model = self.get("model") if self.get("model") is not None else None 
                print("[ControllerAgent] Sending ECG data...")
                msg = Message(to="segmenter@localhost")
                msg.body = json.dumps({
                    "signal": self.agent.normalized_signal,
                    "model": model
                })
                await self.send(msg)
                print("[ControllerAgent] 📨 Sent data to SegmentationAgent")

                # Wait for response
                response = None
                timeout = 60  # seconds
                interval = 0.5  # polling interval
                elapsed = 0

                while elapsed < timeout:
                    response = await self.receive(timeout=interval)
                    if response:
                        break
                    elapsed += interval

                if response:
                    print("[ControllerAgent] ✅ Received response from SegmentationAgent")
                    self.agent.mask = json.loads(response.body)["full_prediction"]
                    
                    # full_prediction
                else:
                    print("[ControllerAgent] ❌ No response from SegmentationAgent")


                if 2 not in steps:
                    self.agent.final_result.update(json.loads(response.body))
                    print("[ControllerAgent] Final result got")
                    self.agent.result_ready.set()

            #print(self.agent)
            
            if 2 in steps:
                print("[ControllerAgent] Sending detection data to PostDetectionAgent...")
                msg = Message(to="post_detection@localhost")
                msg.body = json.dumps({
                    "signal": self.agent.normalized_signal,
                    "mask": self.agent.mask
                })
                await self.send(msg)
                print("[ControllerAgent] 📨 Sent data to PostDetectionAgent")

                # Wait for responseresponse = None
                timeout = 30  # seconds
                interval = 0.5  # polling interval
                elapsed = 0

                while elapsed < timeout:
                    response = await self.receive(timeout=interval)
                    if response:
                        break
                    elapsed += interval
                if response:
                    print("[ControllerAgent] ✅ Received response from PostDetectionAgent")
                else:
                    print("[ControllerAgent] ❌ No response from PostDetectionAgent")


                self.agent.mask = json.loads(response.body)["full_prediction"]
                self.agent.final_result.update(json.loads(response.body))
                if 3 not in steps:
                    print("[ControllerAgent] Final result got")
                    self.agent.result_ready.set()   


            
            if 3 in steps:
                print("[ControllerAgent] Sending detection data to FeaturesAgent...")
                msg = Message(to="feature@localhost")
                msg.body = json.dumps({
                    "signal": self.agent.normalized_signal,
                    "mask": self.agent.mask
                })
                await self.send(msg)
                print("[ControllerAgent] 📨 Sent data to FeaturesAgent")

                # Wait for response
                response = None
                timeout = 30  # seconds
                interval = 0.5  # polling interval
                elapsed = 0

                while elapsed < timeout:
                    response = await self.receive(timeout=interval)
                    if response:
                        break
                    elapsed += interval
                if response:
                    print("[ControllerAgent] ✅ Received response from FeaturesAgent")
                else:
                    print("[ControllerAgent] ❌ No response from FeaturesAgent")

                
                    
                self.agent.final_result.update(json.loads(response.body))
                self.agent.features = json.loads(response.body)["features"]
                print("[ControllerAgent] Features received:", len(self.agent.features))
                    
                    # Check if no beats were detected
                if len(self.agent.features) == 0:
                        print("[ControllerAgent] ℹ️ No beats detected, skipping beat classification")
                        self.agent.final_result.update({
                            "features": [],
                            "status": "no_beats"
                        })
                        self.agent.result_ready.set()
                        return

                if 4 not in steps:
                    print("[ControllerAgent] Final result got")
                    self.agent.result_ready.set()

            if 4 in steps:
                print("[ControllerAgent] Sending features to BeatClassifierAgent...")
                msg = Message(to="beat_classifier@localhost")
                msg.body = json.dumps({
                    "features": self.agent.features
                })
                await self.send(msg)
                print("[ControllerAgent] 📨 Sent data to BeatClassifierAgent")

                # Wait for response
                response = None
                timeout = 30  # seconds
                interval = 0.5  # polling interval
                elapsed = 0

                while elapsed < timeout:
                    response = await self.receive(timeout=interval)
                    if response:
                        break
                    elapsed += interval

                if response:
                    print("[ControllerAgent] ✅ Received response from BeatClassifierAgent")
                    response_data = json.loads(response.body)
                    
                    # Check if no beats were detected
                    if response_data.get("status") == "no_beats":
                        print("[ControllerAgent] ℹ️ No beats detected in classification")
                        self.agent.final_result.update({
                            "features": [],
                            "status": "no_beats"
                        })
                        print("[ControllerAgent] Final result got")
                        self.agent.result_ready.set()
                else:
                    print("[ControllerAgent] ❌ No response from BeatClassifierAgent")

                self.agent.final_result.update(json.loads(response.body))
                if 5 not in steps:
                    print("[ControllerAgent] Final result got")
                    self.agent.result_ready.set()

            if 5 in steps:
                print("[ControllerAgent] Sending features to NormalVsAbnormalAgent...")
                msg = Message(to="normal_vs_abnormal@localhost")
                msg.body = json.dumps({
                    "name": self.get("name"),
                    "normalized_signal": self.agent.normalized_signal,
                    "full_prediction": self.agent.mask,
                    "features": self.agent.final_result["features"]
                })
                await self.send(msg)
                print("[ControllerAgent] 📨 Sent data to NormalVsAbnormalAgent")

                # Wait for response
                response = None
                timeout = 30  # seconds
                interval = 0.5  # polling interval
                elapsed = 0

                while elapsed < timeout:
                    response = await self.receive(timeout=interval)
                    if response:
                        break
                    elapsed += interval
                if response:
                    print("[ControllerAgent] ✅ Received response from NormalVsAbnormalAgent")
                else:
                    print("[ControllerAgent] ❌ No response from NormalVsAbnormalAgent")

                self.agent.final_result.update(json.loads(response.body))
                
                # If the signal is abnormal, send it to the sinus bradycardia classifier
                if self.agent.final_result["signal_type"] == "Abnormal":
                    print("[ControllerAgent] Signal is abnormal, sending to SinusBradycardiaClassifierAgent...")
                    msg = Message(to="sinus_bradycardia_classifier@localhost")
                    msg.body = json.dumps({
                        "name": self.get("name"),
                        "normalized_signal": self.agent.normalized_signal,
                        "full_prediction": self.agent.mask,
                        "features": self.agent.final_result["features"]
                    })
                    await self.send(msg)
                    print("[ControllerAgent] 📨 Sent data to SinusBradycardiaClassifierAgent")

                    # Wait for response
                    response = None
                    timeout = 30  # seconds
                    interval = 0.5  # polling interval
                    elapsed = 0

                    while elapsed < timeout:
                        response = await self.receive(timeout=interval)
                        if response:
                            break
                        elapsed += interval
                    if response:
                        print("[ControllerAgent] ✅ Received response from SinusBradycardiaClassifierAgent")
                        # Update the signal type with the more specific classification
                        self.agent.final_result["signal_type"] = json.loads(response.body)["signal_type"]
                    else:
                        print("[ControllerAgent] ❌ No response from SinusBradycardiaClassifierAgent")

                if 6 not in steps:
                    print("[ControllerAgent] Final result got")
                    self.agent.result_ready.set()

            if 6 in steps:
                print("[ControllerAgent] start saving data")
                
                msg = Message(to="storage@localhost")
                print("[ControllerAgent] name is ", self.get("name"))
                msg.body = json.dumps({
                    "name": self.get("name"),
                    "normalized_signal": self.agent.normalized_signal,
                    "full_prediction": self.agent.mask,
                    "features": self.agent.final_result["features"],
                    "signal_type": self.agent.final_result["signal_type"],
                    "signal_features": self.agent.final_result["signal_features"]
                })
                await self.send(msg)
                # Wait for response
                response = None
                timeout = 30  # seconds
                interval = 0.5  # polling interval
                elapsed = 0

                while elapsed < timeout:
                    response = await self.receive(timeout=interval)
                    if response:
                        break
                    elapsed += interval
                if response:
                    print("[ControllerAgent] ✅ Received response from Storage agent")
                else:
                    print("[ControllerAgent] ❌ No response from Storage agent")

                self.agent.result_ready.set()    
                print("[ControllerAgent] Saved signal mask and features data")

            
       

    async def setup(self):
        print(f"[{self.jid}] ControllerAgent ready.")
        #self.add_behaviour(self.PipelineManager())
