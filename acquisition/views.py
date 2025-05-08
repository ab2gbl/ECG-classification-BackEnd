from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import asyncio

from .agents_manager import run_agent_pipeline  # You define this


class FullDetectionView(APIView):
    def post(self, request):
        ecg_dat = request.data.get("ecg_dat")
        ecg_hea = request.data.get("ecg_hea")
        name = request.data.get("name") if request.data.get("name") is not None else "unknown"
        model = request.data.get("model")
        start_step = int(request.data.get("start_step")) if request.data.get("start_step") is not None else 0
        end_step = int(request.data.get("end_step")) if request.data.get("end_step") is not None else 4
        signal_start = int(request.data.get("signal_start")) if request.data.get("signal_start") is not None else 0
        signal_end = int(request.data.get("signal_end")) if request.data.get("signal_end") is not None else 10
        print("got file")
        try:
            result = asyncio.run(run_agent_pipeline(name,ecg_dat,ecg_hea,signal_start,signal_end,model,start_step,end_step))  # Call the agent system
            if result == "No response":
                return Response({"status": "error", "message": "No response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"status": "success", "result": result},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

