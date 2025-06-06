import numpy as np
import pandas as pd
from tqdm import tqdm
from tensorflow.keras.models import load_model
import mlflow
import globals_vars
mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")

R_detection_run_id = globals_vars.get_R_detection()
R_model = mlflow.keras.load_model(f"runs:/{R_detection_run_id}/model")
print("R_model loaded successfully")
def preprocess_qrs_wave(wave, target_length=250):
    wave = wave.astype(np.float32)
    # Normalize
    wave = (wave - np.mean(wave)) / (np.std(wave) + 1e-8)
    # Pad or truncate to target length
    if len(wave) < target_length:
        wave = np.pad(wave, (0, target_length - len(wave)), mode='constant')
    else:
        wave = wave[:target_length]
    return wave.reshape(1, -1, 1)

def extract_features_per_qrs(signal ,mask, fs=250):

    #model_path = os.path.join(os.path.dirname(__file__), "models", "R_detection.h5")
    #R_model = load_model(model_path)
    features_list = []
    #time = np.arange(len(signal)) / fs
    n = len(signal)

    # Find all QRS starts
    
    qrs_mask = (mask == 2).astype(np.int8)
    transitions = np.diff(qrs_mask, prepend=0)
    qrs_starts = np.flatnonzero(transitions == 1)
    qrs_ends = np.flatnonzero(transitions == -1) - 1

    if len(qrs_ends) < len(qrs_starts):
        qrs_ends = np.append(qrs_ends, n - 1)
    
    previous_r_index = None  # To calculate RR interval

    for i in tqdm(range(len(qrs_starts)), desc="extract features"):
        f = {}
        # Add beat number (1-based indexing)
        f['beat_number'] = i + 1
        

        p_wave = np.array([])
        qrs_wave = np.array([])
        t_wave = np.array([])
        p_indices = np.array([])
        t_indices = np.array([])

        qrs_start = qrs_starts[i]
        # Find QRS end within the current segment
        qrs_end = qrs_ends[i]
        next_qrs_start = qrs_starts[i+1] if i < len(qrs_starts) - 1 else len(mask)

        
        qrs_indices = np.arange(qrs_start, qrs_end + 1)[mask[qrs_start:qrs_end+1] == 2]
        
        if len(qrs_indices) <= 1:
            continue
        
        # Search for the P wave just before this QRS (no QRS or T in between)
        start_idx = qrs_ends[i-1]-1 if i > 0 else 0
        p_indices = np.where(mask[start_idx:qrs_start] == 1)[0]+start_idx
        valid_p = []
        for p_end in reversed(p_indices):
                if np.all(mask[p_end:qrs_start] != 2) and np.all(mask[p_end:qrs_start] != 3):
                    p_start = p_end
                    while p_start > 0 and mask[p_start - 1] == 1:
                        p_start -= 1
                    valid_p = list(range(p_start, p_end + 1))
                    break

        # Search for the T wave just after this QRS (no QRS or P in between)

        t_indices = np.where(mask[qrs_end:next_qrs_start] == 3)[0]
        t_indices = t_indices + (qrs_end )
        
        valid_t = []
        for t_start_offset in t_indices:
            t_start = t_start_offset
            if np.all(mask[qrs_end+1:t_start] != 2) and np.all(mask[qrs_end+1:t_start] != 1):
                #print("got t")
                t_end = t_start
                while t_end < len(mask) - 1 and mask[t_end + 1] == 3:
                    t_end += 1
                valid_t = list(range(t_start, t_end + 1))
                break
        # Extract samples
        valid_p = [i for i in valid_p if i < len(signal)]
        p_wave = signal[valid_p] if valid_p else np.array([])
        
        qrs_indices = [i for i in qrs_indices if i < len(signal)]
        if len(qrs_indices) <= 1:
            continue
        
        qrs_indices = np.array(qrs_indices)
        
        qrs_wave = signal[qrs_indices]
        valid_t = [i for i in valid_t if i < len(signal)]
        t_wave = signal[valid_t] if valid_t else np.array([])
        p_indices = valid_p if valid_p else np.array([])
        t_indices = valid_t if valid_t else np.array([])
        
        padding = 0
        
        if len(p_wave)>0:
          f['start'] = p_indices[0]-padding if p_indices[0] > padding else 0
          
        else :
          f['start'] = qrs_indices[0]-padding if qrs_indices[0] > padding else 0

        if len(t_wave)>0:
          f['end'] = t_indices[-1]+padding if t_indices[-1] < len(signal)-padding else len(signal)
          
        else :
          f['end'] = qrs_indices[-1]+padding if qrs_indices[-1] < len(signal)-padding else len(signal)


        p_start,p_end,t_start,t_end = None,None,None,None
        if len(p_wave)>0:
            p_start = p_indices[0]
            p_end = p_indices[-1]
        if len(t_wave)>0:
            t_start = t_indices[0]
            t_end = t_indices[-1]
        f['qrs_start'] = qrs_indices[0]
        f['qrs_end'] =  qrs_indices[-1]
        f['p_start'] = p_start
        f['p_end'] =  p_end
        f['t_start'] = t_start
        f['t_end'] =  t_end
        


        f['Duree_P_ms'] = len(p_wave) / fs * 1000 if len(p_wave) > 0 else 0
        f['Duree_QRS_ms'] = len(qrs_wave) / fs * 1000 if len(qrs_wave) > 0 else 0
        f['Duree_T_ms'] = len(t_wave) / fs * 1000 if len(t_wave) > 0 else 0

        f['Intervalle_PR_ms'] = ((qrs_start - valid_p[0]) / fs * 1000) if valid_p else 0
        f['Intervalle_QT_ms'] = ((valid_t[-1] - qrs_start) / fs * 1000) if valid_t else 0
        f['Intervalle_ST_ms'] = ((valid_t[0] - qrs_end) / fs * 1000) if valid_t else 0


        # Amplitude_P
        if len(p_wave) > 0:
          default_start = (p_wave[0]+p_wave[-1])/2 if len(p_wave) > 0 else 0
          p_index = p_indices[np.argmax(np.abs(signal[p_indices]-default_start))]
          p_amplitude = signal[p_index]
          f['P_index']= p_index
          f['Amplitude_P'] = p_amplitude
        else:
          f['P_index']= 0
          f['Amplitude_P'] = 0

        # Amplitude_R
        all_wave = signal[int(f['start']):int(f['end'])]
        all_indices = range(int(f['start']),int(f['end']))
        R_window_input = preprocess_qrs_wave(all_wave)
        prediction = R_model.predict(R_window_input,verbose=0)[0]  
        # Find predicted R-peak
        predicted_r_relative = np.argmax(prediction)
       
        if (predicted_r_relative>len(range(all_indices[0],qrs_indices[-1]))):
            r_index = qrs_indices[-1]
        else:
            predicted_r_relative = min(predicted_r_relative,len(all_indices)-1)
            r_index = all_indices[predicted_r_relative]
        
        r_amplitude = signal[r_index]

        f['R_index']= r_index# Preprocess qrs_wave the same way as during training


        f['Amplitude_R'] = r_amplitude
        # RR interval
        if previous_r_index is not None:
            f['Intervalle_RR_ms'] = (r_index - previous_r_index) / fs * 1000
        else:
            f['Intervalle_RR_ms'] = np.nan   # Or np.nan if you prefer

        # Update previous_r_index for next beat
        previous_r_index = r_index

        # --- Detect Q and S waves relative to R ---
        q_index, s_index = None, None
        q_amplitude, s_amplitude = None, None

        if r_amplitude > np.median(signal[qrs_indices]):  # R is a max peak
            q_candidates = qrs_indices[qrs_indices < r_index]
            s_candidates = qrs_indices[qrs_indices > r_index]
            if len(q_candidates) > 0:
                q_index = q_candidates[np.argmin(signal[q_candidates])]
                q_amplitude = signal[q_index]
            if len(s_candidates) > 0:
                s_index = s_candidates[np.argmin(signal[s_candidates])]
                s_amplitude = signal[s_index]
        else:  # R is a min peak
            q_candidates = qrs_indices[qrs_indices < r_index]
            s_candidates = qrs_indices[qrs_indices > r_index]
            if len(q_candidates) > 0:
                q_index = q_candidates[np.argmax(signal[q_candidates])]
                q_amplitude = signal[q_index]
            if len(s_candidates) > 0:
                s_index = s_candidates[np.argmax(signal[s_candidates])]
                s_amplitude = signal[s_index]

        # Add Q and S info
        f['Q_index'] = q_index if q_index is not None else 0
        f['Amplitude_Q'] = q_amplitude if q_amplitude is not None else 0
        f['S_index'] = s_index if s_index is not None else 0
        f['Amplitude_S'] = s_amplitude if s_amplitude is not None else 0


        # Amplitude_T
        if len(t_wave) > 0:
          default_start = (t_wave[0]+t_wave[-1])/2 if len(t_wave) > 0 else 0
          # print(default_start)
          t_index = t_indices[np.argmax(np.abs(signal[t_indices]-default_start))]
          t_amplitude = signal[t_index]
          f['T_index']= t_index
          f['Amplitude_T'] = t_amplitude
        else:
          f['T_index']= 0
          f['Amplitude_T'] = 0

        # Amplitude Ratio
        f['T/R_ratio'] = np.max(np.abs(t_wave)) / np.max(np.abs(qrs_wave)) if len(t_wave) > 0 and len(qrs_wave) > 0 else 0
        f['P/R_ratio'] = np.max(np.abs(p_wave)) / np.max(np.abs(qrs_wave)) if len(p_wave) > 0 and len(qrs_wave) > 0 else 0


        # Pente (slopes)
        f['QRS_area'] = np.trapz(np.abs(qrs_wave), dx=1/fs)

        # QR Slope
        if q_index is not None and q_index < r_index:
            delta_qr = (r_amplitude - q_amplitude)
            time_qr = (r_index - q_index) / fs
            f['Slope_QR'] = delta_qr / time_qr if time_qr != 0 else 0
        else:
            f['Slope_QR'] = 0

        # RS Slope
        if s_index is not None and r_index < s_index:
            delta_rs = (s_amplitude - r_amplitude)
            time_rs = (s_index - r_index) / fs
            f['Slope_RS'] = delta_rs / time_rs if time_rs != 0 else 0
        else:
            f['Slope_RS'] = 0

        # --- P wave symmetry ---
        if len(p_wave) > 2:
            mid = len(p_wave) // 2
            left = p_wave[:mid]
            right = p_wave[mid:]
            f['P_symmetry'] = 1 - abs(np.mean(left) - np.mean(right)) / (np.mean(left) + 1e-6)
        else:
            f['P_symmetry'] = 0

        # --- T wave inversion ---
        if len(t_wave) > 0:
            f['T_inversion'] = int(np.sign(f['Amplitude_T']) != np.sign(f['Amplitude_R']))
        else:
            f['T_inversion'] = -1

        # --- QRS axis estimate ---
        axis_indicator = (abs(f['Amplitude_R']) - abs(f['Amplitude_S']) + abs(f['Amplitude_Q'])) / (
            abs(f['Amplitude_R']) + abs(f['Amplitude_S']) + abs(f['Amplitude_Q']) + 1e-6)

        f['QRS_axis_estimate'] = axis_indicator

        # Heart rate
        if pd.notna(f['Intervalle_RR_ms']) and f['Intervalle_RR_ms'] > 0:
            f['Heart_rate_bpm'] = 60000 / f['Intervalle_RR_ms']
        else:
            f['Heart_rate_bpm'] = np.nan  # or 0 if your pipeline prefers

        # Premature beat detection (basic heuristic)
        recent_rrs = [
            beat['Intervalle_RR_ms'] 
            for beat in features_list[-3:] 
            if pd.notna(beat['Intervalle_RR_ms']) and beat['Intervalle_RR_ms'] > 0
        ]

        if len(recent_rrs) >= 2:
            mean_rr = np.mean(recent_rrs)
            f['Premature_beat'] = int(f['Intervalle_RR_ms'] < 0.8 * mean_rr)
        else:
            f['Premature_beat'] = 0



        #  Rhythm Features

        # Local rhythm variability (SDNN)
        f['Local_RR_variability'] = np.std(recent_rrs) if len(recent_rrs) > 1 else 0

        # RMSSD (local)
        if len(recent_rrs) > 2:
            diffs = np.diff(recent_rrs)
            f['Local_RMSSD'] = np.sqrt(np.mean(diffs**2))
        else:
            f['Local_RMSSD'] = 0

        # Bigeminy / Trigeminy pattern
        all_rrs = [
            beat['Intervalle_RR_ms']
            for beat in features_list[-5:]
            if pd.notna(beat['Intervalle_RR_ms']) and beat['Intervalle_RR_ms'] > 0
        ]
        if len(all_rrs) >= 4:
            pattern = (np.array(all_rrs) < 0.9 * np.mean(all_rrs)).astype(int)
            pattern_str = ''.join(map(str, pattern))
            f['Bigeminy'] = int('10' in pattern_str)
            f['Trigeminy'] = int('110' in pattern_str)
        else:
            f['Bigeminy'] = 0
            f['Trigeminy'] = 0
        

        features_list.append(f)


    return features_list


