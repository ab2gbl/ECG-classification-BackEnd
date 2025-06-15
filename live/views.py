from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import wfdb
import os
import tempfile
from acquisition.agents.acquisition_agent import bandpass_filter, smooth_signal, normalize_signal , resample_signal
class ECGUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        dat_file = request.FILES.get('dat_file')
        hea_file = request.FILES.get('hea_file')

        if not dat_file or not hea_file:
            return Response({"error": "Both .dat and .hea files are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Save to a temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            hea_bytes = hea_file.read()
            dat_bytes = dat_file.read()

            # Get the real base name from the .hea content
            first_line = hea_bytes.decode().splitlines()[0]
            true_base_name = first_line.split()[0]
            base_path = os.path.join(tmp_dir, true_base_name)
    
            # Save both files
            with open(base_path + ".hea", "wb") as f:
                f.write(hea_bytes)
            with open(base_path + ".dat", "wb") as f:
                f.write(dat_bytes)

            try:
                
                try:
                    # Try to read all 15 channels (requires .xyz file to exist)
                    record = wfdb.rdrecord(base_path)
                except FileNotFoundError:
                    # If .xyz file is missing, fall back to first 12 channels (standard ECG)
                    record = wfdb.rdrecord(base_path, channels=list(range(12)))
                signal = record.p_signal[:, 0]  # lead I
                fs = record.fs
                end = 1800
                if end > len(signal)/fs:
                    end = len(signal)/fs
                ecg_signal=signal[0:int(end*fs)]
                if fs != 250:
                    ecg_signal = resample_signal(ecg_signal, original_fs=fs, target_fs=250)
                    fs = 250
                filtered_signal = bandpass_filter(ecg_signal,fs=fs)
                smoothed_signal = smooth_signal(filtered_signal)
                normalized_signal = normalize_signal(smoothed_signal)
                
                    

                return Response({
                    "signal": normalized_signal.tolist(),
                    "fs": record.fs
                }, status=200)
            except Exception as e:
                return Response({"error": str(e)}, status=500)
