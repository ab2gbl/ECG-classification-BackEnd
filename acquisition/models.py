from django.db import models
import json
from django.utils import timezone

# Create your models here.

class Signal(models.Model):
    name = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    normalized_signal = models.TextField()  # Store as JSON string
    mask = models.TextField()  # Store as JSON string
    disease = models.CharField(max_length=255, null=True, blank=True)  # Can be null, blank, or contain disease name
    
    class Meta:
        unique_together = ('name', 'timestamp')  # Make name and timestamp together unique
    
    def natural_key(self):
        return (self.name, self.timestamp)
    
    def set_normalized_signal(self, signal_array):
        self.normalized_signal = json.dumps(signal_array)
    
    def get_normalized_signal(self):
        return json.loads(self.normalized_signal)
    
    def set_mask(self, mask_array):
        self.mask = json.dumps(mask_array)
    
    def get_mask(self):
        return json.loads(self.mask)
    
    def __str__(self):
        return f"{self.name} at {self.timestamp}"

class BeatFeatures(models.Model):
    signal_name = models.ForeignKey(Signal, on_delete=models.CASCADE, related_name='beat_features')
    beat_number = models.IntegerField(default=0)  # Add beat number field with default value
    
    # Wave boundaries
    start = models.IntegerField()
    end = models.IntegerField()
    qrs_start = models.IntegerField()
    qrs_end = models.IntegerField()
    p_start = models.IntegerField()
    p_end = models.IntegerField()
    t_start = models.IntegerField()
    t_end = models.IntegerField()
    
    # Durations
    duree_p_ms = models.FloatField()
    duree_qrs_ms = models.FloatField()
    duree_t_ms = models.FloatField()
    intervalle_pr_ms = models.FloatField()
    intervalle_qt_ms = models.FloatField()
    intervalle_st_ms = models.FloatField()
    
    # Wave indices and amplitudes
    p_index = models.IntegerField()
    amplitude_p = models.FloatField()
    r_index = models.IntegerField()
    amplitude_r = models.FloatField()
    intervalle_rr_ms = models.FloatField()
    q_index = models.IntegerField()
    amplitude_q = models.FloatField()
    s_index = models.IntegerField()
    amplitude_s = models.FloatField()
    t_index = models.IntegerField()
    amplitude_t = models.FloatField()
    
    # Ratios and areas
    t_r_ratio = models.FloatField()
    p_r_ratio = models.FloatField()
    qrs_area = models.FloatField()
    
    # Slopes and symmetry
    slope_qr = models.FloatField()
    slope_rs = models.FloatField()
    p_symmetry = models.FloatField()
    
    # Additional features
    t_inversion = models.IntegerField()
    qrs_axis_estimate = models.FloatField()
    heart_rate_bpm = models.FloatField()
    premature_beat = models.IntegerField()
    local_rr_variability = models.FloatField()
    local_rmssd = models.FloatField()
    bigeminy = models.IntegerField()
    trigeminy = models.IntegerField()
    type = models.CharField(max_length=1)
    
    def __str__(self):
        return f"Beat {self.beat_number } Features for {self.signal_name.name} at {self.signal_name.timestamp}"


class SignalFeatures(models.Model):
    signal_name = models.ForeignKey(Signal, on_delete=models.CASCADE, related_name='signal_features')
    
    # QRS Duration Statistics
    duree_qrs_ms_mean = models.FloatField()
    duree_qrs_ms_std = models.FloatField()
    duree_qrs_ms_min = models.FloatField()
    duree_qrs_ms_max = models.FloatField()
    
    # P Wave Duration Statistics
    duree_p_ms_mean = models.FloatField()
    duree_p_ms_std = models.FloatField()
    duree_p_ms_min = models.FloatField()
    duree_p_ms_max = models.FloatField()
    
    # T Wave Duration Statistics
    duree_t_ms_mean = models.FloatField()
    duree_t_ms_std = models.FloatField()
    duree_t_ms_min = models.FloatField()
    duree_t_ms_max = models.FloatField()
    
    # QT Interval Statistics
    intervalle_qt_ms_mean = models.FloatField()
    intervalle_qt_ms_std = models.FloatField()
    intervalle_qt_ms_min = models.FloatField()
    intervalle_qt_ms_max = models.FloatField()
    
    # PR Interval Statistics
    intervalle_pr_ms_mean = models.FloatField()
    intervalle_pr_ms_std = models.FloatField()
    intervalle_pr_ms_min = models.FloatField()
    intervalle_pr_ms_max = models.FloatField()
    
    # ST Interval Statistics
    intervalle_st_ms_mean = models.FloatField()
    intervalle_st_ms_std = models.FloatField()
    intervalle_st_ms_min = models.FloatField()
    intervalle_st_ms_max = models.FloatField()
    
    # P Wave Amplitude Statistics
    amplitude_p_mean = models.FloatField()
    amplitude_p_std = models.FloatField()
    amplitude_p_min = models.FloatField()
    amplitude_p_max = models.FloatField()
    
    # Q Wave Amplitude Statistics
    amplitude_q_mean = models.FloatField()
    amplitude_q_std = models.FloatField()
    amplitude_q_min = models.FloatField()
    amplitude_q_max = models.FloatField()
    
    # R Wave Amplitude Statistics
    amplitude_r_mean = models.FloatField()
    amplitude_r_std = models.FloatField()
    amplitude_r_min = models.FloatField()
    amplitude_r_max = models.FloatField()
    
    # S Wave Amplitude Statistics
    amplitude_s_mean = models.FloatField()
    amplitude_s_std = models.FloatField()
    amplitude_s_min = models.FloatField()
    amplitude_s_max = models.FloatField()
    
    # T Wave Amplitude Statistics
    amplitude_t_mean = models.FloatField()
    amplitude_t_std = models.FloatField()
    amplitude_t_min = models.FloatField()
    amplitude_t_max = models.FloatField()
    
    # T/R Ratio Statistics
    t_r_ratio_mean = models.FloatField()
    t_r_ratio_std = models.FloatField()
    t_r_ratio_min = models.FloatField()
    t_r_ratio_max = models.FloatField()
    
    # P/R Ratio Statistics
    p_r_ratio_mean = models.FloatField()
    p_r_ratio_std = models.FloatField()
    p_r_ratio_min = models.FloatField()
    p_r_ratio_max = models.FloatField()
    
    # QRS Area Statistics
    qrs_area_mean = models.FloatField()
    qrs_area_std = models.FloatField()
    qrs_area_min = models.FloatField()
    qrs_area_max = models.FloatField()
    
    # QR Slope Statistics
    slope_qr_mean = models.FloatField()
    slope_qr_std = models.FloatField()
    slope_qr_min = models.FloatField()
    slope_qr_max = models.FloatField()
    
    # RS Slope Statistics
    slope_rs_mean = models.FloatField()
    slope_rs_std = models.FloatField()
    slope_rs_min = models.FloatField()
    slope_rs_max = models.FloatField()
    
    # Heart Rate Statistics
    heart_rate_bpm_mean = models.FloatField()
    heart_rate_bpm_std = models.FloatField()
    heart_rate_bpm_min = models.FloatField()
    heart_rate_bpm_max = models.FloatField()
    
    # Local RMSSD Statistics
    local_rmssd_mean = models.FloatField()
    local_rmssd_std = models.FloatField()
    local_rmssd_min = models.FloatField()
    local_rmssd_max = models.FloatField()
    
    # T Inversion Statistics
    t_inversion_sum = models.IntegerField()
    t_inversion_mean = models.FloatField()
    
    # Premature Beat Count
    premature_beat_sum = models.IntegerField()
    
    # Bigeminy Count
    bigeminy_sum = models.IntegerField()
    
    # Trigeminy Count
    trigeminy_sum = models.IntegerField()

    # Beat Type Counts
    count_N = models.IntegerField(default=0)
    count_L = models.IntegerField(default=0)
    count_R = models.IntegerField(default=0)
    count_slash = models.IntegerField(default=0)  # Using count_slash instead of count_/ for valid field name
    count_V = models.IntegerField(default=0)
    count_else = models.IntegerField(default=0)

    # Beat Type Ratios
    ratio_N = models.FloatField(default=0.0)
    ratio_L = models.FloatField(default=0.0)
    ratio_R = models.FloatField(default=0.0)
    ratio_slash = models.FloatField(default=0.0)  # Using ratio_slash instead of ratio_/ for valid field name
    ratio_V = models.FloatField(default=0.0)
    ratio_else = models.FloatField(default=0.0)

    # Derived Features
    percent_T_inversion = models.FloatField(default=0.0)
    QRS_prolonged_ratio = models.FloatField(default=0.0)
    QT_prolonged_ratio = models.FloatField(default=0.0)
    PVC_ratio = models.FloatField(default=0.0)
    num_beats = models.IntegerField(default=0)
    std_Intervalle_RR_ms = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"Signal Features for {self.signal_name.name} at {self.signal_name.timestamp}"
