from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
class FeatureAgent(Agent):
    class ExtractFeatures(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print("[FeatureAgent] Got segmentation:", msg.body)
                # Extract features
                features = "HR: 72 bpm, PR: 120ms"
                response = Message(to="decision@localhost")
                response.body = msg.body
                await asyncio.sleep(2)
                await self.send(response)

    async def setup(self):
        print(f"[{self.jid}] FeatureAgent started.")
        self.add_behaviour(self.ExtractFeatures())
