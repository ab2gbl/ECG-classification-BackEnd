import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from acquisition.agent_runner import AGENTS

controller = AGENTS["controller"]

class ECGConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("[WebSocket] ✅ Connected")
        self.pipeline = None
        self.is_processing = False
        self.current_request_id = None

    async def disconnect(self, close_code):
        print("[WebSocket] ❌ Disconnected")
        self.is_processing = False
        self.current_request_id = None

    async def process_ecg_data(self, request_id, ecg_chunk):
        """Process ECG data and return result"""
        try:
            
            # Set data for controller agent
            controller.set("normalized_signal", ecg_chunk)
            controller.set("start_step", 1)
            controller.set("end_step", 5)
            controller.reset_result()

            # Create and assign pipeline behavior
            self.pipeline = controller.PipelineManager()
            controller.add_behaviour(self.pipeline)

            print(f"[WebSocket] 🚀 Processing request {request_id}...")
            await controller.result_ready.wait()

            print(f"[ControllerAgent] ✅ Result ready for request {request_id}")
            final_result = controller.final_result
            return final_result if final_result else "No response"

        except Exception as e:
            print(f"[WebSocket] ❌ Error processing request {request_id}:", str(e))
            raise e

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            request_id = data.get("request_id", "unknown")
            ecg_chunk = data.get("signal")
            chunk_name = data.get("chunk_name", "unknown")  # Get chunk name with default value

            # Immediately reject if already processing
            if self.is_processing:
                print(f"[WebSocket] ⚠️ Rejecting request {request_id} - system busy")
                await self.send(text_data=json.dumps({
                    "request_id": request_id,
                    "chunk_name": chunk_name,
                    "status": "error",
                    "message": "System is busy processing another request. Please wait."
                }))
                return

            if not ecg_chunk:
                await self.send(text_data=json.dumps({
                    "request_id": request_id,
                    "chunk_name": chunk_name,
                    "status": "error",
                    "message": "No ECG data provided"
                }))
                return

            # Check minimum chunk size (2 seconds at 250Hz)
            if len(ecg_chunk) < 500:
                await self.send(text_data=json.dumps({
                    "request_id": request_id,
                    "chunk_name": chunk_name,
                    "status": "error",
                    "message": "ECG data chunk is too short. Please send at least 500 samples (2 seconds) of ECG data."
                }))
                return

            # Mark as processing
            self.is_processing = True
            self.current_request_id = request_id

            try:
                print(f"[WebSocket] 🔒 Processing request {request_id} for chunk {chunk_name}")
                
                # Process the ECG data
                result = await self.process_ecg_data(request_id, ecg_chunk)
                
                # Send the result
                await self.send(text_data=json.dumps({
                    "request_id": request_id,
                    "chunk_name": chunk_name,
                    "status": "success",
                    "result": result
                }))
                
            finally:
                self.is_processing = False
                self.current_request_id = None
                print(f"[WebSocket] 🔓 Completed request {request_id} for chunk {chunk_name}")

        except Exception as e:
            print(f"[WebSocket] ❌ Error handling request {request_id}:", str(e))
            await self.send(text_data=json.dumps({
                "request_id": request_id,
                "chunk_name": chunk_name,
                "status": "error",
                "message": str(e)
            }))
            self.is_processing = False
            self.current_request_id = None
