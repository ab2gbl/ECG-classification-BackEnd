from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import asyncio

from .agent_controller import run_agent_pipeline  # You define this

class ProcessECGView(APIView):
    def post(self, request):
        ecg_dat = request.data.get("ecg_dat")
        ecg_hea = request.data.get("ecg_hea")
        print("got file")
        try:
            result = asyncio.run(run_agent_pipeline(ecg_dat,ecg_hea))  # Call the agent system
            if result == "No response":
                return Response({"status": "error", "message": "No response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"status": "success", "result": result},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
