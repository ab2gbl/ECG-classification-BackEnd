from .agents.acquisition_agent import AcquisitionAgent
from .agents.segmentation_agent import SegmentationAgent
from .agents.feature_agent import FeatureAgent
from .agents.decision_agent import DecisionAgent
from spade.message import Message
import asyncio

async def run_agent_pipeline(ecg_dat,ecg_hea):
    # Initialize agents
    a = AcquisitionAgent("acquirer@localhost", "pass")
    s = SegmentationAgent("segmenter@localhost", "pass")
    f = FeatureAgent("feature@localhost", "pass")
    d = DecisionAgent("decision@localhost", "pass")
    a.set("ecg_dat", ecg_dat)
    a.set("ecg_hea", ecg_hea)

    print("starting agents")
    await a.start()
    await s.start()
    await f.start()
    await d.start()
    print("agents started")
    

    # Send ECG data to start the flow
    #msg = Message(to="segmenter@localhost")
    #msg.body = ecg_data
    #await a.send(msg)

    # Receive result from DecisionAgent
    final_msg = await d.behaviours[0].receive(timeout=10)
    final_decision = final_msg.body if final_msg else "No response"

    await a.stop()
    await s.stop()
    await f.stop()
    await d.stop()

    return final_decision
