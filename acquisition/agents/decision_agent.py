from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

class DecisionAgent(Agent):
    class Decide(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print("[DecisionAgent] Features received:", msg.body)
                print("[DecisionAgent] 💡 Decision: Normal ECG")

    async def setup(self):
        print(f"[{self.jid}] DecisionAgent started.")
        self.add_behaviour(self.Decide())
