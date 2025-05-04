from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import wfdb
from scipy.signal import butter, filtfilt
import numpy as np
import tempfile
import os
import asyncio
from scipy.signal import resample
import json
import base64
from spade.template import Template
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
    class WaitForData(CyclicBehaviour):
        
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print("[AcquisitionAgent] 📥 Received ECG data from controller")
                data = json.loads(msg.body)
                dat_bytes = base64.b64decode(data["dat_file"])
                hea_bytes = base64.b64decode(data["hea_file"])
                with tempfile.TemporaryDirectory() as tmpdirname:
                    first_line = hea_bytes.decode().splitlines()[0]  # ✅ no .read()
                    true_base_name = first_line.split()[0]
                    base_path = os.path.join(tmpdirname, true_base_name)
                    with open(base_path + ".dat", "wb") as f:
                        f.write(dat_bytes)
                    with open(base_path + ".hea", "wb") as f:
                        f.write(hea_bytes)
                                            
                    record = wfdb.rdrecord(base_path)

                  # Get the signal (ECG data)
                    signal = record.p_signal[:, 0]  # lead I
                    fs = record.fs
                    start = data['signal_start'] if 'signal_start' in data else 0
                    end = data['signal_end'] if 'signal_end' in data else len(signal)/fs
                    if end > len(signal)/fs:
                        end = len(signal)/fs
                    ecg_signal=signal[int(start*fs):int(end*fs)]
                    #ecg_signal=signal[:]
                    
                    # Optionally apply preprocessing (bandpass filter, smoothing, normalization)
                    filtered_signal = bandpass_filter(ecg_signal,fs=fs)
                    smoothed_signal = smooth_signal(filtered_signal)
                    normalized_signal = normalize_signal(smoothed_signal)
                    if fs != 250:
                        normalized_signal = resample_signal(normalized_signal, original_fs=fs, target_fs=250)
                        fs = 250
                    

                    # Send result back to controller
                    response = msg.make_reply()  # ✅ Key change: Use make_reply()
                    response.set_metadata("performative", "inform")
                    response.set_metadata("content_type", "application/json")
                    response.body = json.dumps({
                        "normalized_signal": normalized_signal.tolist()  # Your processed signal
                    })
                    await self.send(response)
                    print("[AcquisitionAgent] ✅ Sent processed ECG back to controller")
            
            

            
            

    async def setup(self):
        print(f"[{self.jid}] AcquisitionAgent ready and waiting...")
        
        self.add_behaviour(self.WaitForData())        
        