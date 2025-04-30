import numpy as np
from scipy.signal import find_peaks
from tqdm import tqdm
def remove_uncomplete_first_last_wave(predicted):
    """
    Merge or remove close-together same-class segments if separated only by background.
    :param predicted: 1D numpy array of predicted class labels (0=background, 1=P, 2=QRS, 3=T)
    :param target_class: 1 for P, 3 for T
    :return: modified predicted array
    """
    start = predicted[0]
    end = predicted[-1]
    if start != 0:
      i=0
      while i < len(predicted) and predicted[i]==start:
        i+=1
      predicted[:i]=0
    if end != 0:
      i=len(predicted)-1
      while i > -1 and predicted[i]==end:
        i-=1
      predicted[i+1:]=0

    return predicted

def merge_close_waves(predicted, max_gap=10):
  predicted = predicted.copy()
  for target_class in [1,2,3]:
    indices = np.where(predicted == target_class)[0]

    if len(indices) < 2:
        return predicted  # Nothing to merge

    for i in range(len(indices) - 1):
        current = indices[i]
        next_ = indices[i + 1]
        #print(next_-current-1)
        if 0 < next_ - current - 1 < max_gap:
            # Fill the gap between current and next with 1s
            predicted[current:next_ + 1] = target_class



  return predicted


def remove_irrelevant_waves(predicted,start_search=2,end_search=5):
    """
    Remove waves before the first P and after the last T that are not relevant.
    :param predicted: 1D numpy array of predicted class labels (0=background, 1=P, 2=QRS, 3=T)
    :return: modified predicted array
    """
    # print(predicted)

    start=0
    # Step 1: Find the first P that has a QRS after it
    if 1 in predicted[:start_search*250] :
      # print("found p in first 2s")

      for i in range(len(predicted)-1):
          start = i

          if predicted[i] == 1:
              start = i
              # skip 1
              while i < len(predicted)-1 and predicted[i] == 1:
                i += 1
              # if it's not 0 or 2 break
              if predicted[i] == 3:
                continue
              # skip background if it exist
              if predicted[i] == 0:
                while i < len(predicted)-1 and predicted[i] == 0:
                  i += 1
              # if it's not qrs continue to next p
              if predicted[i] != 2:
                continue
              else:
                break
      #print("start:",start)
      predicted[:start] = 0


    # step 2 : remove after last T
    if 3 in predicted[-end_search*250:]:
      # print("found t in last 5s")

      end = predicted[-1]
      for i in range((len(predicted) - 1), -1, -1):
          end = i

          if predicted[i] == 3:
              end = i
              # skip 1
              while i > 0 and predicted[i] == 3:
                i -= 1
              # if it's not 0 or 2 break
              if predicted[i] == 1:
                #print("found 1")
                continue
              # skip background if it exist
              if predicted[i] == 0:
                while i > 0 and predicted[i] == 0:
                  i -= 1
              # if it's not qrs continue to next p
              if predicted[i] != 2:
                continue
              else:
                break
      #print("end:",end)
      predicted[end+1:] = 0







    return (predicted)

# Now, i is the index of the first value that is NOT 1 after the P wave segment


def check_repeated_waves(predicted):
    """
    Merge or remove close-together same-class segments if separated only by background.
    :param predicted: 1D numpy array of predicted class labels (0=background, 1=P, 2=QRS, 3=T)
    :param target_class: 1 for P, 3 for T
    :return: modified predicted array
    """
    cleaned = predicted.copy()
    for target_class in [1,2,3]:
      segments = []
      in_segment = False
      start = 0

      # Step 1: Collect all segments of the target class
      for i, val in enumerate(predicted):
          if val == target_class and not in_segment:
              in_segment = True
              start = i
          elif val != target_class and in_segment:
              in_segment = False
              segments.append((start, i - 1))
      if in_segment:
          segments.append((start, len(predicted) - 1))

      # Step 2: Check for pairs of segments with only background (0) in between
      i = 0
      while i < len(segments) - 1:
          s1, e1 = segments[i]
          s2, e2 = segments[i + 1]
          between = cleaned[e1 + 1:s2]

          if np.all(between == 0):  # Only background between them
              len1 = e1 - s1 + 1
              len2 = e2 - s2 + 1

              # Remove the shorter one
              if len1 < len2:
                  cleaned[s1:e1 + 1] = 0
              else:
                  cleaned[s2:e2 + 1] = 0

              # Remove the deleted segment from the list
              segments.pop(i if len1 < len2 else i + 1)
          else:
              i += 1


    return cleaned



def fix_before_P(signal,mask,p_start,p_end,slope_threshold=0.02):
  diff_signal = np.diff([signal[p_start],signal[p_start-5]])  # check around the Q point for slope change
  j = 0
  while True:
    while np.abs(diff_signal[-1]) >= slope_threshold and signal[p_start]>signal[p_start-1] and mask[p_start-1]==0:  # Continue until slope becomes small
        j+=1
        p_start -= 1
        mask[p_start] = 1  # mark as part of the QRS
        diff_signal = np.diff([signal[p_start],signal[p_start-5]])  # re-evaluate slope
    if mask[p_start-1]!=0:
      break
    if j == 0:

        slope_threshold -= 0.001
        #print("slope_threshold: ",slope_threshold)
        if slope_threshold < 0.005:
          break
    else:
        break
  #print ("fixed_before with peak:",j)
  return mask,p_start


def fix_P(signal, mask):
    p_mask = (mask == 1).astype(int)
    qrs_mask = (mask == 2).astype(int)

    transitions = np.diff(p_mask, prepend=0)
    p_starts = np.where(transitions == 1)[0]

    qrs_starts = np.where(np.diff(qrs_mask, prepend=0) == 1)[0]

    fixed_p_info = []

    for i in range(len(p_starts)):

        slope_threshold = 0.02  # arbitrary threshold for slope to be considered small
        p_start = p_starts[i]

        p_next = p_starts[i+1] if i < len(p_starts) - 1 else len(mask)
        p_indices = np.where((mask == 1) & (np.arange(len(mask)) >= p_start) & (np.arange(len(mask)) < p_next))[0]

        p_end = p_indices[-1] if  len(p_indices)>0 else p_start
        #print("p_start,p_end: ",p_start,p_end)
        # Get indices of current P segment
        if len(p_indices) < 3:
            continue

        p_wave = signal[p_indices]

        # Check for peak inside current P segment
        peaks, _ = find_peaks(p_wave, prominence=0.01)
        has_peak = len(peaks) > 0
        peak_index = p_indices[peaks[0]] if has_peak else None

        # If no peak, look after end of P segment
        post_p_peak_index = None
        if has_peak:
          #print("has peak")
          mask, p_start = fix_before_P(signal, mask,p_start,p_end)
          j=0
          #print(p_end)
          while (p_end + 1 < len(signal)) and signal[p_end] > signal[p_start] and mask[p_end + 1] == 0:
            j += 1
            p_end += 1
            mask[p_end] = 1
        if not has_peak:

            # Look ahead to the next QRS start
            next_qrs_start = qrs_starts[qrs_starts > p_end]
            next_qrs_start = next_qrs_start[0] if len(next_qrs_start) > 0 else len(signal)

            # Look AFTER the P segment
            post_range = np.arange(p_start,min(len(signal) ,p_end + 50,  next_qrs_start ))
            post_peaks = []
            if len(post_range) > 3:
                post_wave = signal[post_range]
                peaks, _ = find_peaks(post_wave, prominence=0.01)
                # Filter by mask == 0
                for p in peaks:
                    peak_idx = post_range[p]
                    # Check that the region from p_end to peak_idx is all mask == 0
                    if np.all(mask[p_end+1:peak_idx + 1] == 0):
                        post_peaks.append(peak_idx)


            # Look BEFORE the P segment
            pre_range = np.arange(max(0, p_start - 50), p_end)  # limit the look-back window to ~400ms
            pre_peaks = []
            if len(pre_range) > 3:
                pre_wave = signal[pre_range]
                peaks, _ = find_peaks(pre_wave, prominence=0.01)
                # Filter by mask == 0
                pre_peaks = [pre_range[p] for p in peaks if mask[pre_range[p]] == 0]
                for p in peaks:
                    peak_idx = pre_range[p]
                    # Check that the region from p_end to peak_idx is all mask == 0
                    if np.all(mask[peak_idx + 1:p_start] == 0):
                        pre_peaks.append(peak_idx)

            # Closest peak
            ## Combine both and choose closest properly
            closest_peak = None
            min_distance = float('inf')

            ## Compare post-peaks to p_end
            for peak in post_peaks:
                dist = abs(peak - p_end)
                if dist < min_distance:
                    min_distance = dist
                    closest_peak = peak

            ## Compare pre-peaks to p_start
            for peak in pre_peaks:
                dist = abs(peak - p_start)
                if dist < min_distance:
                    min_distance = dist
                    closest_peak = peak

            post_p_peak_index = closest_peak if closest_peak is not None else None

            peak = None
            if post_p_peak_index is not None:
              if post_p_peak_index < p_start:
                peak = "before"
              else:
                peak = "after"


            #print(peak)
            if peak == "after":
                mask, p_start = fix_before_P(signal, mask,p_start,p_end)
                j=0
                while (p_end + 1 < len(signal)) and signal[p_end] > signal[p_start] and mask[p_end + 1] == 0:
                  j += 1
                  p_end += 1
                  mask[p_end] = 1
            elif peak == "before":

                mask[post_p_peak_index-2:p_start] = 1
                p_start = post_p_peak_index-2
                mask, p_start = fix_before_P(signal, mask,p_start,p_end)


        fixed_p_info.append({
            'start': p_indices[0],
            'end': p_indices[-1],
            'has_peak': has_peak,
            'peak_index': peak_index,
            'post_p_peak_index': post_p_peak_index
        })
        #print (fixed_p_info)

    return mask

def fast_fix_QRS(signal, mask, fs=250):
    time = np.arange(len(signal)) / fs
    indices = np.arange(len(mask))  # Precompute indices array

    # Precompute slopes for QRS start and end adjustments
    slope_start = np.zeros_like(signal)
    slope_start[3:] = signal[3:] - signal[:-3]  # slope[i] = signal[i] - signal[i-3]
    slope_end = np.zeros_like(signal)
    slope_end[:-5] = signal[:-5] - signal[5:]    # slope[i] = signal[i] - signal[i+5]

    qrs_mask = (mask == 2).astype(int)
    transitions = np.diff(qrs_mask, prepend=0)
    qrs_starts = np.where(transitions == 1)[0]

    for i in tqdm(range(len(qrs_starts)), desc="Processing QRS"):
        qrs_start = qrs_starts[i]
        next_qrs_start = qrs_starts[i+1] if i < len(qrs_starts)-1 else len(mask)
        # Find QRS end within the current segment
        qrs_end = next_qrs_start - 1
        while qrs_end >= qrs_start and mask[qrs_end] != 2:
            qrs_end -= 1
        if qrs_end < qrs_start:
            continue  # skip invalid segment

        # Adjust QRS start based on preceding P wave
        p_indices = np.where(mask[:qrs_start] == 1)[0]
        valid_p = []
        if len(p_indices) > 0:
            # Check from the end backwards
            for p_end in reversed(p_indices):
                if np.any(mask[p_end:qrs_start] >= 2):  # Check if any QRS (2) or T-wave (3) exists
                    continue
                p_start = p_end
                while p_start > 0 and mask[p_start-1] == 1:
                    p_start -= 1
                valid_p = np.arange(p_start, p_end + 1)
                break
            if len(valid_p) > 0 and (qrs_start - valid_p[-1]) < 20:
                mask[valid_p[-1]+1:qrs_start] = 2
                qrs_start = valid_p[-1] + 1

        # Adjust QRS start using slope-based backtracking if no P wave found
        if len(valid_p) == 0:
            slope_threshold = 0.02
            max_back_steps = 100  # Prevent infinite loops
            back_steps = 0

            current_start = qrs_start
            while back_steps < max_back_steps and current_start >= 3:
                current_slope = slope_start[current_start]
                if abs(current_slope) < slope_threshold:
                    break
                # Check for peaks in previous 100 samples
                pre_range = slice(max(0, current_start - 100), current_start)
                pre_signal = signal[pre_range]
                if len(pre_signal) < 3:
                    break
                peaks, _ = find_peaks(pre_signal, prominence=0.01)
                if len(peaks) > 0:
                    first_peak = pre_range.start + peaks[0]
                    if current_start <= first_peak:
                        break
                if mask[current_start - 1] != 0:
                    break
                current_start -= 1
                back_steps += 1
                slope_threshold = max(slope_threshold - 0.001, 0.005)
            mask[current_start:qrs_start] = 2
            qrs_start = current_start

        # Adjust QRS end
        # Extend until signal stops descending
        while qrs_end < len(signal)-1 and mask[qrs_end+1] == 0 and signal[qrs_end] >= signal[qrs_end+1]:
            qrs_end += 1
            mask[qrs_end] = 2

        # Further adjust based on slope
        slope_threshold_end = 0.02
        max_forward_steps = 50
        forward_steps = 0
        while (qrs_end < len(signal)-5 and forward_steps < max_forward_steps and 
               abs(slope_end[qrs_end]) >= slope_threshold_end and 
               mask[qrs_end+1] == 0):
            qrs_end += 1
            mask[qrs_end] = 2
            forward_steps += 1
            slope_threshold_end = max(slope_threshold_end - 0.001, 0.005)

    return mask

def post_process_ecg(predicted):

    predicted = remove_uncomplete_first_last_wave(predicted)
    predicted = merge_close_waves(predicted)
    predicted = remove_irrelevant_waves(predicted)
    predicted = check_repeated_waves(predicted)

    return predicted
