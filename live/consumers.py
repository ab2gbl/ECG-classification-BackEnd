import json
from channels.generic.websocket import AsyncWebsocketConsumer
from acquisition.agent_runner import AGENTS

controller = AGENTS["controller"]

class ECGConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("[WebSocket] ✅ Connected")
        self.pipeline = None
        self.is_processing = False  # Flag to block concurrent chunks
        self.final_decision = None

    async def disconnect(self, close_code):
        print("[WebSocket] ❌ Disconnected")
        
    async def receive(self, text_data):
        final_decision = None
        if self.is_processing:
            print("⚠️ Still processing previous chunk, skipping this one...")
            await self.send(text_data=json.dumps({
                "warning": "Still processing previous chunk. Please slow down."
            }))
            return

        data = json.loads(text_data)
        ecg_chunk = data.get("signal")

        if not ecg_chunk:
            await self.send(text_data=json.dumps({"error": "No ECG data provided"}))
            return
        if len(ecg_chunk) < 250 * 60:
            await self.send(text_data=json.dumps({"error": "ECG data chunk is too short, the pc is slow for this "}))
            return
        # Mark as busy
        self.is_processing = True

        try:
            # Set data for controller agent
            controller.set("normalized_signal", ecg_chunk)
            
            controller.set("start_step", 1)
            controller.set("end_step", 4)

            # Create and assign pipeline behavior
            self.pipeline = controller.PipelineManager()
            controller.add_behaviour(self.pipeline)

            print("[WebSocket] 🚀 Running agent pipeline...")
            await controller.result_ready.wait()

            print("[ControllerAgent] ✅ Result ready")
            final_result = controller.final_result
            final_decision = final_result if final_result else "No response"

            await self.send(text_data=json.dumps({
                "result": final_decision
            }))

        except Exception as e:
            print("[WebSocket] ❌ Error:", str(e))
            await self.send(text_data=json.dumps({
                "error": str(e)
            }))

        finally:
            self.is_processing = False  # Allow next chunk
