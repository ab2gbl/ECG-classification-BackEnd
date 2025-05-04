import json
from channels.generic.websocket import AsyncWebsocketConsumer
from acquisition.agents_manager import run_agent_pipeline

class ECGConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("[WebSocket] Connected")

    async def disconnect(self, close_code):
        print("[WebSocket] Disconnected")

    async def receive(self, text_data):
        data = json.loads(text_data)
        ecg_chunk = data.get("signal")

        if not ecg_chunk:
            await self.send(text_data=json.dumps({"error": "No ECG data provided"}))
            return

        # Run your agent pipeline
        try:
            print("[WebSocket] Running agent pipeline...")
            decision = await run_agent_pipeline(
                ecg_dat=ecg_chunk,
                ecg_hea=None,  # You can send this from frontend too if needed
                signal_start=0,
                signal_end=10,
                model=None,  # Or pass in a model name if you want
                start=0,
                end=4  # Full pipeline including decision
            )
            print("[WebSocket] Decision received:", decision)

            # Send back the decision result
            await self.send(text_data=json.dumps({
                "prediction": decision
            }))
        except Exception as e:
            print("[WebSocket] Error:", str(e))
            await self.send(text_data=json.dumps({
                "error": str(e)
            }))
