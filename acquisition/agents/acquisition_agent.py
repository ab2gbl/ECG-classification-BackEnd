from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
import wfdb
from scipy.signal import butter, filtfilt
import numpy as np
import tempfile
import os
import asyncio
from scipy.signal import resample
import json
# Bandpass filter function
def bandpass_filter(signal, lowcut=0.5, highcut=10, fs=250, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)

# Signal smoothing function
def smooth_signal(data, window_size=5):
    window = np.ones(window_size) / window_size
    smoothed = np.convolve(data, window, mode='same')
    return smoothed

# Signal normalization function
def normalize_signal(data):
    return (data - np.mean(data)) / np.std(data)


def resample_signal(signal, original_fs, target_fs):
    num_samples = int(len(signal) * target_fs / original_fs)
    resampled_signal = resample(signal, num_samples)
    return resampled_signal

class AcquisitionAgent(Agent):
    
    # Behaviour to send ECG data
    class SendECGData(OneShotBehaviour):
        def __init__(self, normalized_signal):
            super().__init__()
            self.normalized_signal = normalized_signal

        async def run(self):
            print("[AcquisitionAgent] Sending ECG data...")
            msg = Message(to="segmenter@localhost")  # Assuming this is the correct recipient
            normalized_signal = self.normalized_signal
            #print(type(normalized_signal), normalized_signal.shape)
            #print(normalized_signal[:10])  # Just to make sure it's real data

            
            msg.body = json.dumps(normalized_signal.tolist())  # ✅ this will now work#msg.body = str(self.normalized_signal)  # Sending data as a string (or you could use pickling for more complex data)
            #print("msg body: ", msg.body)
            await asyncio.sleep(2)
            await self.send(msg)

    async def setup(self):
        print(f"[{self.jid}] AcquisitionAgent ready.")

        ecg_dat_file = self.get("ecg_dat")  # InMemoryUploadedFile
        ecg_hea_file = self.get("ecg_hea")  # InMemoryUploadedFile

        try:
            # Create a temporary directory to hold the files
            with tempfile.TemporaryDirectory() as tmpdirname:
                # Peek into the uploaded .hea file to get the base name (like "100")
                first_line = ecg_hea_file.read().decode().splitlines()[0]
                true_base_name = first_line.split()[0]

                # Reset file pointer to beginning for saving
                ecg_hea_file.seek(0)
                ecg_dat_file.seek(0)

                base_path = os.path.join(tmpdirname, true_base_name)
                with open(base_path + ".hea", "wb") as f:
                    f.write(ecg_hea_file.read())

                with open(base_path + ".dat", "wb") as f:
                    f.write(ecg_dat_file.read())

                # Now this will work
                record = wfdb.rdrecord(base_path)


                
                # Get the signal (ECG data)
                signal = record.p_signal[:, 0]  # lead I
                fs = record.fs
                ecg_signal=signal[(0):(10*fs)]
                
                # Optionally apply preprocessing (bandpass filter, smoothing, normalization)
                filtered_signal = bandpass_filter(ecg_signal)
                smoothed_signal = smooth_signal(filtered_signal)
                normalized_signal = normalize_signal(smoothed_signal)
                if fs != 250:
                    normalized_signal = resample_signal(normalized_signal, original_fs=fs, target_fs=250)
                    fs = 250
                
                # Send the processed data
                self.add_behaviour(self.SendECGData(normalized_signal))
        
        except Exception as e:
            print(f"Error loading ECG data: {e}")

