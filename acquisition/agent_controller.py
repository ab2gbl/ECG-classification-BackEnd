from .agents.acquisition_agent import AcquisitionAgent
from .agents.segmentation_agent import SegmentationAgent
from .agents.feature_agent import FeatureAgent
from .agents.decision_agent import DecisionAgent
from .agents.controller_agent import ControllerAgent
from spade.message import Message
import asyncio

async def run_agent_pipeline(ecg_dat,ecg_hea):
    # Initialize agents
    a = AcquisitionAgent("acquirer@localhost", "pass")
    s = SegmentationAgent("segmenter@localhost", "pass")
    f = FeatureAgent("feature@localhost", "pass")
    d = DecisionAgent("decision@localhost", "pass")
    c = ControllerAgent("controller@localhost", "pass")
    c.set("ecg_dat", ecg_dat)
    c.set("ecg_hea", ecg_hea)
    c.set("start_step", 0)
    c.set("end_step", 1)
    print("starting agents")
    await a.start()
    await s.start()
    await f.start()
    await d.start()
    await c.start()
    print("agents started")
    

    # Send ECG data to start the flow
    #msg = Message(to="segmenter@localhost")
    #msg.body = ecg_data
    #await a.send(msg)

    # Receive result from DecisionAgent
    await c.result_ready.wait()
    print("[ControllerAgent] result_ready, waiting for final result...")
    final_result = c.final_result
    print("[ControllerAgent] Final result received")
    final_decision = final_result if final_result else "No response"
    print("[ControllerAgent] Pipeline completed")

    await a.stop()
    await s.stop()
    await f.stop()
    await d.stop()
    await c.stop()
    print("agents stopped")
    return final_decision
