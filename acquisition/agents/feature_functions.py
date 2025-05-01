import numpy as np
from scipy.stats import skew, kurtosis, entropy
from scipy.signal import find_peaks
from tqdm import tqdm


def extract_features_per_qrs(signal ,mask, fs=250):
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

        p_wave = np.array([])
        qrs_wave = np.array([])
        t_wave = np.array([])
        p_indices = np.array([])
        t_indices = np.array([])


        qrs_start = qrs_starts[i]
        # Find QRS end within the current segment
        qrs_end = qrs_ends[i]
        next_qrs_start = qrs_starts[i+1] if i < len(qrs_starts) - 1 else len(mask)

        # Get current QRS region
        qrs_indices = np.arange(qrs_start, qrs_end + 1)[mask[qrs_start:qrs_end+1] == 2]
        #print("qrs_indices:",qrs_indices)
        if len(qrs_indices) == 0:
            continue
        #print("qrs_start,end:",qrs_start,qrs_end)isnt

        # Search for the P wave just before this QRS (no QRS or T in between)
        start_idx = qrs_ends[i-1]-1 if i > 0 else 0
        p_indices = np.where(mask[start_idx:qrs_start] == 1)[0]+start_idx
        #p_indices = np.where(mask[:qrs_start] == 1)[0]
        valid_p = []
        for p_end in reversed(p_indices):
                if np.all(mask[p_end:qrs_start] != 2) and np.all(mask[p_end:qrs_start] != 3):
                    p_start = p_end
                    while p_start > 0 and mask[p_start - 1] == 1:
                        p_start -= 1
                    valid_p = list(range(p_start, p_end + 1))
                    break

        #print("p start,end:",valid_p[0],valid_p[-1])

        #
        # Search for the T wave just after this QRS (no QRS or P in between)

        t_indices = np.where(mask[qrs_end:next_qrs_start] == 3)[0]
        t_indices = t_indices + (qrs_end )
        #print("t_indices:",t_indices)

        valid_t = []
        for t_start_offset in t_indices:
            t_start = t_start_offset
            #print("mask[qrs_end:t_start]:",mask[qrs_end:t_start])
            if np.all(mask[qrs_end+1:t_start] != 2) and np.all(mask[qrs_end+1:t_start] != 1):
                #print("got t")
                t_end = t_start
                while t_end < len(mask) - 1 and mask[t_end + 1] == 3:
                    t_end += 1
                valid_t = list(range(t_start, t_end + 1))
                break
        # Extract samples
        p_wave = signal[valid_p] if valid_p else np.array([])
        qrs_wave = signal[qrs_indices]
        t_wave = signal[valid_t] if valid_t else np.array([])
        p_indices = valid_p if valid_p else np.array([])
        t_indices = valid_t if valid_t else np.array([])
        #print("p_wave,qrs_wave,t_wave:",len(p_wave),len(qrs_wave),len(t_wave))
        #print("p_indices,t_indices:",len(p_indices),len(t_indices))

        # Build features per beat
        f = {}
        padding = 0
        if len(p_wave)>0:
          f['start'] = p_indices[0]-padding if p_indices[0] > padding else 0
        else :
          f['start'] = qrs_indices[0]-padding if qrs_indices[0] > padding else 0

        if len(t_wave)>0:
          f['end'] = t_indices[-1]+padding if t_indices[-1] < len(signal)-padding else len(signal)
        else :
          f['end'] = qrs_indices[-1]+padding if qrs_indices[-1] < len(signal)-padding else len(signal)



        f['Duree_P_ms'] = len(p_wave) / fs * 1000 if len(p_wave) > 0 else 0
        f['Duree_QRS_ms'] = len(qrs_wave) / fs * 1000 if len(qrs_wave) > 0 else 0
        f['Duree_T_ms'] = len(t_wave) / fs * 1000 if len(t_wave) > 0 else 0

        f['Intervalle_PR_ms'] = ((qrs_start - valid_p[0]) / fs * 1000) if valid_p else 0
        f['Intervalle_QT_ms'] = ((valid_t[-1] - qrs_start) / fs * 1000) if valid_t else 0
        f['Intervalle_ST_ms'] = ((valid_t[0] - qrs_end) / fs * 1000) if valid_t else 0


        # Amplitude_P
        if len(p_wave) > 0:
          default_start = (p_wave[0]+p_wave[-1])/2 if len(p_wave) > 0 else 0
          #print(default_start)
          p_index = p_indices[np.argmax(np.abs(signal[p_indices]-default_start))]
          p_amplitude = signal[p_index]
          f['P_index']= p_index
          f['Amplitude_P'] = p_amplitude
        else:
          f['P_index']= 0
          f['Amplitude_P'] = 0

        # Amplitude_R
        #default_start = p_wave[0] if len(p_wave) > 0 else signal[qrs_start]
        '''
        pre_start = max(0, qrs_start - 100)
            pre_wave = signal[pre_start:qrs_start]
            
            # Find first valid peak before QRS
            first_peak_before_qrs = None
            if len(pre_wave) > 3:
                peaks, _ = find_peaks(pre_wave, prominence=0.01)
                for p in peaks:
                    if mask[pre_start + p] == 0:
                        # print("found peak before qrs")
                        first_peak_before_qrs = pre_start + p
                        break
        '''
        
        
        
        # Find first valid peak before QRS
        # Find both positive and negative peaks
        pos_peaks, _ = find_peaks(qrs_wave, prominence=0.01)
        neg_peaks, _ = find_peaks(-qrs_wave, prominence=0.01)
        peaks = np.sort(np.concatenate((pos_peaks, neg_peaks)))
        
        
        if len(peaks) > 0:
            default_start = (qrs_wave[0] + qrs_wave[-1]) / 2
            r_index = qrs_indices[peaks[np.argmax(np.abs(qrs_wave[peaks] - default_start))]]  # most prominent
        else:
            default_start = (qrs_wave[0] + qrs_wave[-1]) / 2
            r_index = qrs_indices[np.argmax(np.abs(signal[qrs_indices] - default_start))]


        
        
        r_amplitude = signal[r_index]

        f['R_index']= r_index
        f['Amplitude_R'] = r_amplitude
        # RR interval
        if previous_r_index is not None:
            f['Intervalle_RR_ms'] = (r_index - previous_r_index) / fs * 1000
        else:
            f['Intervalle_RR_ms'] = 0  # Or np.nan if you prefer

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
        f['Heart_rate_bpm'] = 60000 / f['Intervalle_RR_ms'] if f['Intervalle_RR_ms'] > 0 else 0

        # Premature beat detection (basic heuristic)
        recent_rrs = [beat['Intervalle_RR_ms'] for beat in features_list[-3:] if beat['Intervalle_RR_ms'] > 0]
        if len(recent_rrs) >= 2:
            mean_rr = np.mean(recent_rrs)
            f['Premature_beat'] = int(f['Intervalle_RR_ms'] < 0.8 * mean_rr)
        else:
            f['Premature_beat'] = 0



        #  Rhythm Features
        # Heart rate
        f['Heart_rate_bpm'] = 60000 / f['Intervalle_RR_ms'] if f['Intervalle_RR_ms'] > 0 else 0

        # Rhythm Features
        recent_rrs = [beat['Intervalle_RR_ms'] for beat in features_list[-3:] if beat['Intervalle_RR_ms'] > 0]
        if len(recent_rrs) >= 2:
            mean_rr = np.mean(recent_rrs)
            f['Premature_beat'] = int(f['Intervalle_RR_ms'] < 0.8 * mean_rr)
        else:
            f['Premature_beat'] = 0

        # Local rhythm variability (SDNN)
        f['Local_RR_variability'] = np.std(recent_rrs) if len(recent_rrs) > 1 else 0

        # RMSSD (local)
        if len(recent_rrs) > 2:
            diffs = np.diff(recent_rrs)
            f['Local_RMSSD'] = np.sqrt(np.mean(diffs**2))
        else:
            f['Local_RMSSD'] = 0

        # Bigeminy / Trigeminy pattern
        all_rrs = [beat['Intervalle_RR_ms'] for beat in features_list[-5:] if beat['Intervalle_RR_ms'] > 0]
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
