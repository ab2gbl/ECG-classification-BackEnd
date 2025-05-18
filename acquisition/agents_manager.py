#from .agents.acquisition_agent import AcquisitionAgent
#from .agents.segmentation_agent import SegmentationAgent
#from .agents.feature_agent import FeatureAgent
from .agents.controller_agent import ControllerAgent
#from .agents.post_detection_agent import PostDetectionAgent
from spade.message import Message
import asyncio
from .agent_runner import AGENTS
from .agents.controller_agent import ControllerAgent
async def run_agent_pipeline(name,ecg_dat,ecg_hea,signal_start=0,signal_end=10,model=None,start=0,end=1):
    
    controller = AGENTS["controller"]
    controller.set("name", name)
    controller.set("ecg_dat", ecg_dat)
    controller.set("ecg_hea", ecg_hea)
    controller.set("model", model) if model else controller.set("model", None)
    controller.set("start_step", start)
    controller.set("end_step", end )
    controller.set("signal_start", signal_start)
    controller.set("signal_end", signal_end)
    controller.reset_result()
    print("result_ready:",controller.result_ready)
    pipeline = controller.PipelineManager()
    controller.add_behaviour(pipeline)
    await controller.result_ready.wait()
    print("[ControllerAgent] result_ready, waiting for final result...")
    final_result = controller.final_result
    final_decision = final_result if final_result else "No response"


    print("[ControllerAgent] Pipeline completed")
    
    print("agents stopped")
    print("return now")
    return final_decision
    print("return didnt work")

