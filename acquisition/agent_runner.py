# agents_app/agent_runner.py

import asyncio
from .agents.acquisition_agent import AcquisitionAgent
from .agents.segmentation_agent import SegmentationAgent
from .agents.feature_agent import FeatureAgent
from .agents.beat_classifier_agent import BeatClassifierAgent
from .agents.post_detection_agent import PostDetectionAgent
from .agents.controller_agent import ControllerAgent
from .agents.storage_agent import StorageAgent
from .agents.normal_vs_abnormal_agent import NormalVsAbnormalAgent
from .agents.sinus_bradycardia_classifier_agent import SinusBradycardiaClassifierAgent
import atexit

    #AGENTS["acquisition"] = AcquisitionAgent("acquirer@localhost", "pass")
    #AGENTS["segmenter"] = SegmentationAgent("segmenter@localhost", "pass")
    #AGENTS["post_detection"] = PostDetectionAgent("post_detection@localhost", "pass")
    #AGENTS["feature"] = FeatureAgent("feature@localhost", "pass")
    #AGENTS["beat_classifier"] = BeatClassifierAgent("beat_classifier@localhost", "pass")
    #AGENTS["controller"] = ControllerAgent("controller@localhost", "pass")

# agents_app/agent_runner.py

import asyncio
import atexit
from typing import Dict, Any
from spade.agent import Agent

AGENTS: Dict[str, Agent] = {}  # Global registry of agents

def start_agents_in_background():
    """Start agents once (idempotent). Safe to call multiple times."""
    if not _agents_initialized():
        asyncio.run(start_agents())

async def start_agents():
    """Initialize and start agents only if they don't exist or are stopped."""
    global AGENTS

    # Initialize agents only if they don't exist
    if "acquisition" not in AGENTS:
        AGENTS["acquisition"] = AcquisitionAgent("acquirer@localhost", "pass")
    if "segmenter" not in AGENTS:
        AGENTS["segmenter"] = SegmentationAgent("segmenter@localhost", "pass")
    if "post_detection" not in AGENTS:
        AGENTS["post_detection"] = PostDetectionAgent("post_detection@localhost", "pass")
    if "feature" not in AGENTS:
        AGENTS["feature"] = FeatureAgent("feature@localhost", "pass")
    if "beat_classifier" not in AGENTS:
        AGENTS["beat_classifier"] = BeatClassifierAgent("beat_classifier@localhost", "pass")
    if "normal_vs_abnormal" not in AGENTS:
        AGENTS["normal_vs_abnormal"] = NormalVsAbnormalAgent("normal_vs_abnormal@localhost", "pass")
    if "sinus_bradycardia_classifier" not in AGENTS:
        AGENTS["sinus_bradycardia_classifier"] = SinusBradycardiaClassifierAgent("sinus_bradycardia_classifier@localhost", "pass")
    if "storage" not in AGENTS:
        AGENTS["storage"] = StorageAgent("storage@localhost", "pass")
    if "controller" not in AGENTS:
        AGENTS["controller"] = ControllerAgent("controller@localhost", "pass")
    
    # Start agents only if not already running
    for name, agent in AGENTS.items():
        if not agent.is_alive():
            await agent.start()
            #print(f"[AgentRunner] Started {name} agent ({agent.jid})")
        else:
            print(f"[AgentRunner] Agent {name} ({agent.jid}) is already running")

def _agents_initialized() -> bool:
    """Check if agents have been initialized at least once."""
    return bool(AGENTS)

@atexit.register
def shutdown_agents():
    """Gracefully stop all agents on exit."""
    print("[AgentRunner] Shutting down agents...")
    for agent in AGENTS.values():
        try:
            if agent.is_alive():
                asyncio.run(agent.stop())
                print(f"[AgentRunner] Stopped {agent.jid}")
        except Exception as e:
            print(f"[AgentRunner] Error stopping {agent.jid}: {e}")
    AGENTS.clear()