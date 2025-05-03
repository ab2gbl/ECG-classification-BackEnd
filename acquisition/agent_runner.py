# agents_app/agent_runner.py

import asyncio
from .agents.acquisition_agent import AcquisitionAgent
from .agents.segmentation_agent import SegmentationAgent
from .agents.feature_agent import FeatureAgent
from .agents.decision_agent import DecisionAgent
from .agents.post_detection_agent import PostDetectionAgent
import atexit
AGENTS = {}

def start_agents_in_background():
    asyncio.run(start_agents())

async def start_agents():
    global AGENTS
    
    AGENTS["acquisition"] = AcquisitionAgent("acquirer@localhost", "pass")
    AGENTS["segmenter"] = SegmentationAgent("segmenter@localhost", "pass")
    AGENTS["post_detection"] = PostDetectionAgent("post_detection@localhost", "pass")
    AGENTS["feature"] = FeatureAgent("feature@localhost", "pass")
    # AGENTS["decision"] = DecisionAgent("decision@localhost", "pass")
    # AGENTS["controller"] = DecisionAgent("controller@localhost", "pass")

    print("[AgentRunner] Starting agents...")

    for agent in AGENTS.values():
        await agent.start()
    
    print("[AgentRunner] All agents started.")


@atexit.register
def shutdown_agents():
    print("[AgentRunner] Shutting down agents...")
    for agent in AGENTS.values():
        try:
            asyncio.run(agent.stop())
        except Exception as e:
            print(f"[AgentRunner] Error stopping agent: {e}")
    #asyncio.run(quit_spade())
    print("[AgentRunner] All agents stopped.")

