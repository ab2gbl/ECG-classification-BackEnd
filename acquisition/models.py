from django.db import models
import json
from django.utils import timezone

# Create your models here.

class Signal(models.Model):
    name = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    normalized_signal = models.TextField()  # Store as JSON string
    mask = models.TextField()  # Store as JSON string
    
    class Meta:
        unique_together = ('name', 'timestamp')  # Make name and timestamp together unique
    
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

class SignalFeatures(models.Model):
    signal_name = models.ForeignKey(Signal, on_delete=models.CASCADE, related_name='features')
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
        return f"Features for {self.signal_name.name} at {self.signal_name.timestamp}"
