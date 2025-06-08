from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import asyncio
from .models import Signal, BeatFeatures, SignalFeatures
from django.core.serializers import serialize
import json
from django.utils.dateparse import parse_datetime

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


class GetSignalsView(APIView):
    def get(self, request):
        try:
            # Get all signals from the database
            signals = Signal.objects.all().order_by('-timestamp')
            
            # Format the response data
            signals_data = []
            for signal in signals:
                signals_data.append({
                    'name': signal.name,
                    'timestamp': signal.timestamp,
                    'disease': signal.disease
                })
            
            return Response({
                'status': 'success',
                'signals': signals_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetSignalView(APIView):
    def get(self, request):
        try:
            # Get parameters from request
            name = request.GET.get('name')
            timestamp_str = request.GET.get('timestamp')
            
            if not name or not timestamp_str:
                return Response({
                    'status': 'error',
                    'message': 'Both name and timestamp are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Parse timestamp
            timestamp = parse_datetime(timestamp_str)
            if not timestamp:
                return Response({
                    'status': 'error',
                    'message': 'Invalid timestamp format'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get signal
            try:
                signal = Signal.objects.get(name=name, timestamp=timestamp)
            except Signal.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Signal not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get beat features
            beat_features = BeatFeatures.objects.filter(signal_name=signal)
            beat_features_data = []
            for beat in beat_features:
                beat_features_data.append({
                    'beat_number': beat.beat_number,
                    'start': beat.start,
                    'end': beat.end,
                    'qrs_start': beat.qrs_start,
                    'qrs_end': beat.qrs_end,
                    'p_start': beat.p_start,
                    'p_end': beat.p_end,
                    't_start': beat.t_start,
                    't_end': beat.t_end,
                    'Duree_P_ms': beat.duree_p_ms,
                    'Duree_QRS_ms': beat.duree_qrs_ms,
                    'Duree_T_ms': beat.duree_t_ms,
                    'Intervalle_PR_ms': beat.intervalle_pr_ms,
                    'Intervalle_QT_ms': beat.intervalle_qt_ms,
                    'Intervalle_ST_ms': beat.intervalle_st_ms,
                    'P_index': beat.p_index,
                    'Amplitude_P': beat.amplitude_p,
                    'R_index': beat.r_index,
                    'Amplitude_R': beat.amplitude_r,
                    'Intervalle_RR_ms': beat.intervalle_rr_ms,
                    'Q_index': beat.q_index,
                    'Amplitude_Q': beat.amplitude_q,
                    'S_index': beat.s_index,
                    'Amplitude_S': beat.amplitude_s,
                    'T_index': beat.t_index,
                    'Amplitude_T': beat.amplitude_t,
                    'T/R_ratio': beat.t_r_ratio,
                    'P/R_ratio': beat.p_r_ratio,
                    'QRS_area': beat.qrs_area,
                    'Slope_QR': beat.slope_qr,
                    'Slope_RS': beat.slope_rs,
                    'P_symmetry': beat.p_symmetry,
                    'T_inversion': beat.t_inversion,
                    'QRS_axis_estimate': beat.qrs_axis_estimate,
                    'Heart_rate_bpm': beat.heart_rate_bpm,
                    'Premature_beat': beat.premature_beat,
                    'Local_RR_variability': beat.local_rr_variability,
                    'Local_RMSSD': beat.local_rmssd,
                    'Bigeminy': beat.bigeminy,
                    'Trigeminy': beat.trigeminy,
                    'Type': beat.type
                })
            
            # Get signal features
            try:
                signal_features = SignalFeatures.objects.get(signal_name=signal)
                signal_features_data = {
                    'duree_qrs_ms_mean': signal_features.duree_qrs_ms_mean,
                    'duree_qrs_ms_std': signal_features.duree_qrs_ms_std,
                    'duree_qrs_ms_min': signal_features.duree_qrs_ms_min,
                    'duree_qrs_ms_max': signal_features.duree_qrs_ms_max,
                    'duree_p_ms_mean': signal_features.duree_p_ms_mean,
                    'duree_p_ms_std': signal_features.duree_p_ms_std,
                    'duree_p_ms_min': signal_features.duree_p_ms_min,
                    'duree_p_ms_max': signal_features.duree_p_ms_max,
                    'duree_t_ms_mean': signal_features.duree_t_ms_mean,
                    'duree_t_ms_std': signal_features.duree_t_ms_std,
                    'duree_t_ms_min': signal_features.duree_t_ms_min,
                    'duree_t_ms_max': signal_features.duree_t_ms_max,
                    'intervalle_qt_ms_mean': signal_features.intervalle_qt_ms_mean,
                    'intervalle_qt_ms_std': signal_features.intervalle_qt_ms_std,
                    'intervalle_qt_ms_min': signal_features.intervalle_qt_ms_min,
                    'intervalle_qt_ms_max': signal_features.intervalle_qt_ms_max,
                    'intervalle_pr_ms_mean': signal_features.intervalle_pr_ms_mean,
                    'intervalle_pr_ms_std': signal_features.intervalle_pr_ms_std,
                    'intervalle_pr_ms_min': signal_features.intervalle_pr_ms_min,
                    'intervalle_pr_ms_max': signal_features.intervalle_pr_ms_max,
                    'intervalle_st_ms_mean': signal_features.intervalle_st_ms_mean,
                    'intervalle_st_ms_std': signal_features.intervalle_st_ms_std,
                    'intervalle_st_ms_min': signal_features.intervalle_st_ms_min,
                    'intervalle_st_ms_max': signal_features.intervalle_st_ms_max,
                    'amplitude_p_mean': signal_features.amplitude_p_mean,
                    'amplitude_p_std': signal_features.amplitude_p_std,
                    'amplitude_p_min': signal_features.amplitude_p_min,
                    'amplitude_p_max': signal_features.amplitude_p_max,
                    'amplitude_q_mean': signal_features.amplitude_q_mean,
                    'amplitude_q_std': signal_features.amplitude_q_std,
                    'amplitude_q_min': signal_features.amplitude_q_min,
                    'amplitude_q_max': signal_features.amplitude_q_max,
                    'amplitude_r_mean': signal_features.amplitude_r_mean,
                    'amplitude_r_std': signal_features.amplitude_r_std,
                    'amplitude_r_min': signal_features.amplitude_r_min,
                    'amplitude_r_max': signal_features.amplitude_r_max,
                    'amplitude_s_mean': signal_features.amplitude_s_mean,
                    'amplitude_s_std': signal_features.amplitude_s_std,
                    'amplitude_s_min': signal_features.amplitude_s_min,
                    'amplitude_s_max': signal_features.amplitude_s_max,
                    'amplitude_t_mean': signal_features.amplitude_t_mean,
                    'amplitude_t_std': signal_features.amplitude_t_std,
                    'amplitude_t_min': signal_features.amplitude_t_min,
                    'amplitude_t_max': signal_features.amplitude_t_max,
                    't_r_ratio_mean': signal_features.t_r_ratio_mean,
                    't_r_ratio_std': signal_features.t_r_ratio_std,
                    't_r_ratio_min': signal_features.t_r_ratio_min,
                    't_r_ratio_max': signal_features.t_r_ratio_max,
                    'p_r_ratio_mean': signal_features.p_r_ratio_mean,
                    'p_r_ratio_std': signal_features.p_r_ratio_std,
                    'p_r_ratio_min': signal_features.p_r_ratio_min,
                    'p_r_ratio_max': signal_features.p_r_ratio_max,
                    'qrs_area_mean': signal_features.qrs_area_mean,
                    'qrs_area_std': signal_features.qrs_area_std,
                    'qrs_area_min': signal_features.qrs_area_min,
                    'qrs_area_max': signal_features.qrs_area_max,
                    'slope_qr_mean': signal_features.slope_qr_mean,
                    'slope_qr_std': signal_features.slope_qr_std,
                    'slope_qr_min': signal_features.slope_qr_min,
                    'slope_qr_max': signal_features.slope_qr_max,
                    'slope_rs_mean': signal_features.slope_rs_mean,
                    'slope_rs_std': signal_features.slope_rs_std,
                    'slope_rs_min': signal_features.slope_rs_min,
                    'slope_rs_max': signal_features.slope_rs_max,
                    'heart_rate_bpm_mean': signal_features.heart_rate_bpm_mean,
                    'heart_rate_bpm_std': signal_features.heart_rate_bpm_std,
                    'heart_rate_bpm_min': signal_features.heart_rate_bpm_min,
                    'heart_rate_bpm_max': signal_features.heart_rate_bpm_max,
                    'local_rmssd_mean': signal_features.local_rmssd_mean,
                    'local_rmssd_std': signal_features.local_rmssd_std,
                    'local_rmssd_min': signal_features.local_rmssd_min,
                    'local_rmssd_max': signal_features.local_rmssd_max,
                    't_inversion_mean': signal_features.t_inversion_mean,
                    't_inversion_sum': signal_features.t_inversion_sum,
                    'premature_beat_sum': signal_features.premature_beat_sum,
                    'bigeminy_sum': signal_features.bigeminy_sum,
                    'trigeminy_sum': signal_features.trigeminy_sum,
                    'count_n': signal_features.count_N,
                    'count_l': signal_features.count_L,
                    'count_r': signal_features.count_R,
                    'count_/': signal_features.count_slash,
                    'count_v': signal_features.count_V,
                    'count_else': signal_features.count_else,
                    'ratio_n': signal_features.ratio_N,
                    'ratio_l': signal_features.ratio_L,
                    'ratio_r': signal_features.ratio_R,
                    'ratio_/': signal_features.ratio_slash,
                    'ratio_v': signal_features.ratio_V,
                    'ratio_else': signal_features.ratio_else,
                    'percent_t_inversion': signal_features.percent_T_inversion,
                    'qrs_prolonged_ratio': signal_features.QRS_prolonged_ratio,
                    'qt_prolonged_ratio': signal_features.QT_prolonged_ratio,
                    'pvc_ratio': signal_features.PVC_ratio,
                    'num_beats': signal_features.num_beats,
                    'std_intervalle_rr_ms': signal_features.std_Intervalle_RR_ms
                }
            except SignalFeatures.DoesNotExist:
                signal_features_data = None
            
            # Prepare response
            response_data = {
                'status': 'success',
                'result': {
                    'normalized_signal': signal.get_normalized_signal(),
                    'full_prediction': signal.get_mask(),
                    'features': beat_features_data,
                    'signal_features': signal_features_data,
                    'signal_type': signal.disease if signal.disease else 'Normal'
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

