from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from asgiref.sync import sync_to_async
import json
from django.utils import timezone

from acquisition.models import Signal, BeatFeatures, SignalFeatures  # Updated model names

class StorageAgent(Agent):
    class StoreResults(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                print("[StorageAgent] 📥 Received message to store signal")
                try:
                    data = json.loads(msg.body)
                    await self.agent.save_to_db(data)
                    print("[StorageAgent] ✅ Data saved")
                    status = "Data saved"
                
                except Exception as e:
                    print(f"[StorageAgent] ❌ Error saving data: {e}")
                    status = "error"

                response =  Message(to="controller@localhost")
                response.body = status
                await self.send(response)
            

    async def setup(self):
        print(f"[{self.jid}] StorageAgent ready.")
        self.add_behaviour(self.StoreResults())

    @sync_to_async
    def save_to_db(self, data):
        name = data["name"]
        print("[StorageAgent] 🔧 Saving to DB... ", name)
        # Save the main signal
        signal = Signal(
            name=name,
            timestamp=timezone.now(),
            disease=data.get("signal_type", "Normal")  # Get signal type from data
        )
        signal.set_normalized_signal(data["normalized_signal"])
        signal.set_mask(data["full_prediction"])
        signal.save()

        # Save individual beat features
        print(f"[StorageAgent] 🔍 Saving beat features, len: {len(data['features'])}")

        for feature in data["features"]:
            BeatFeatures.objects.create(
                signal_name=signal,  # Django will handle the composite key relationship
                beat_number=feature["beat_number"],
                start=feature["start"],
                end=feature["end"],
                qrs_start=feature["qrs_start"],
                qrs_end=feature["qrs_end"],
                p_start=feature["p_start"],
                p_end=feature["p_end"],
                t_start=feature["t_start"],
                t_end=feature["t_end"],
                duree_p_ms=feature["Duree_P_ms"],
                duree_qrs_ms=feature["Duree_QRS_ms"],
                duree_t_ms=feature["Duree_T_ms"],
                intervalle_pr_ms=feature["Intervalle_PR_ms"],
                intervalle_qt_ms=feature["Intervalle_QT_ms"],
                intervalle_st_ms=feature["Intervalle_ST_ms"],
                p_index=feature["P_index"],
                amplitude_p=feature["Amplitude_P"],
                r_index=feature["R_index"],
                amplitude_r=feature["Amplitude_R"],
                intervalle_rr_ms=feature["Intervalle_RR_ms"],
                q_index=feature["Q_index"],
                amplitude_q=feature["Amplitude_Q"],
                s_index=feature["S_index"],
                amplitude_s=feature["Amplitude_S"],
                t_index=feature["T_index"],
                amplitude_t=feature["Amplitude_T"],
                t_r_ratio=feature["T/R_ratio"],
                p_r_ratio=feature["P/R_ratio"],
                qrs_area=feature["QRS_area"],
                slope_qr=feature["Slope_QR"],
                slope_rs=feature["Slope_RS"],
                p_symmetry=feature["P_symmetry"],
                t_inversion=feature["T_inversion"],
                qrs_axis_estimate=feature["QRS_axis_estimate"],
                heart_rate_bpm=feature["Heart_rate_bpm"],
                premature_beat=feature["Premature_beat"],
                local_rr_variability=feature["Local_RR_variability"],
                local_rmssd=feature["Local_RMSSD"],
                bigeminy=feature["Bigeminy"],
                trigeminy=feature["Trigeminy"],
                type=feature["Type"]
            )

        # Save signal features
        print(f"[StorageAgent] 🔍 Saving signal features")
        if "signal_features" in data:
            signal_features = data["signal_features"]
            SignalFeatures.objects.create(
                signal_name=signal,  # Django will handle the composite key relationship
                # QRS Duration Statistics
                duree_qrs_ms_mean=signal_features["duree_qrs_ms_mean"],
                duree_qrs_ms_std=signal_features["duree_qrs_ms_std"],
                duree_qrs_ms_min=signal_features["duree_qrs_ms_min"],
                duree_qrs_ms_max=signal_features["duree_qrs_ms_max"],
                
                # P Wave Duration Statistics
                duree_p_ms_mean=signal_features["duree_p_ms_mean"],
                duree_p_ms_std=signal_features["duree_p_ms_std"],
                duree_p_ms_min=signal_features["duree_p_ms_min"],
                duree_p_ms_max=signal_features["duree_p_ms_max"],
                
                # T Wave Duration Statistics
                duree_t_ms_mean=signal_features["duree_t_ms_mean"],
                duree_t_ms_std=signal_features["duree_t_ms_std"],
                duree_t_ms_min=signal_features["duree_t_ms_min"],
                duree_t_ms_max=signal_features["duree_t_ms_max"],
                
                # QT Interval Statistics
                intervalle_qt_ms_mean=signal_features["intervalle_qt_ms_mean"],
                intervalle_qt_ms_std=signal_features["intervalle_qt_ms_std"],
                intervalle_qt_ms_min=signal_features["intervalle_qt_ms_min"],
                intervalle_qt_ms_max=signal_features["intervalle_qt_ms_max"],
                
                # PR Interval Statistics
                intervalle_pr_ms_mean=signal_features["intervalle_pr_ms_mean"],
                intervalle_pr_ms_std=signal_features["intervalle_pr_ms_std"],
                intervalle_pr_ms_min=signal_features["intervalle_pr_ms_min"],
                intervalle_pr_ms_max=signal_features["intervalle_pr_ms_max"],
                
                # ST Interval Statistics
                intervalle_st_ms_mean=signal_features["intervalle_st_ms_mean"],
                intervalle_st_ms_std=signal_features["intervalle_st_ms_std"],
                intervalle_st_ms_min=signal_features["intervalle_st_ms_min"],
                intervalle_st_ms_max=signal_features["intervalle_st_ms_max"],
                
                # P Wave Amplitude Statistics
                amplitude_p_mean=signal_features["amplitude_p_mean"],
                amplitude_p_std=signal_features["amplitude_p_std"],
                amplitude_p_min=signal_features["amplitude_p_min"],
                amplitude_p_max=signal_features["amplitude_p_max"],
                
                # Q Wave Amplitude Statistics
                amplitude_q_mean=signal_features["amplitude_q_mean"],
                amplitude_q_std=signal_features["amplitude_q_std"],
                amplitude_q_min=signal_features["amplitude_q_min"],
                amplitude_q_max=signal_features["amplitude_q_max"],
                
                # R Wave Amplitude Statistics
                amplitude_r_mean=signal_features["amplitude_r_mean"],
                amplitude_r_std=signal_features["amplitude_r_std"],
                amplitude_r_min=signal_features["amplitude_r_min"],
                amplitude_r_max=signal_features["amplitude_r_max"],
                
                # S Wave Amplitude Statistics
                amplitude_s_mean=signal_features["amplitude_s_mean"],
                amplitude_s_std=signal_features["amplitude_s_std"],
                amplitude_s_min=signal_features["amplitude_s_min"],
                amplitude_s_max=signal_features["amplitude_s_max"],
                
                # T Wave Amplitude Statistics
                amplitude_t_mean=signal_features["amplitude_t_mean"],
                amplitude_t_std=signal_features["amplitude_t_std"],
                amplitude_t_min=signal_features["amplitude_t_min"],
                amplitude_t_max=signal_features["amplitude_t_max"],
                
                # T/R Ratio Statistics
                t_r_ratio_mean=signal_features["t_r_ratio_mean"],
                t_r_ratio_std=signal_features["t_r_ratio_std"],
                t_r_ratio_min=signal_features["t_r_ratio_min"],
                t_r_ratio_max=signal_features["t_r_ratio_max"],
                
                # P/R Ratio Statistics
                p_r_ratio_mean=signal_features["p_r_ratio_mean"],
                p_r_ratio_std=signal_features["p_r_ratio_std"],
                p_r_ratio_min=signal_features["p_r_ratio_min"],
                p_r_ratio_max=signal_features["p_r_ratio_max"],
                
                # QRS Area Statistics
                qrs_area_mean=signal_features["qrs_area_mean"],
                qrs_area_std=signal_features["qrs_area_std"],
                qrs_area_min=signal_features["qrs_area_min"],
                qrs_area_max=signal_features["qrs_area_max"],
                
                # QR Slope Statistics
                slope_qr_mean=signal_features["slope_qr_mean"],
                slope_qr_std=signal_features["slope_qr_std"],
                slope_qr_min=signal_features["slope_qr_min"],
                slope_qr_max=signal_features["slope_qr_max"],
                
                # RS Slope Statistics
                slope_rs_mean=signal_features["slope_rs_mean"],
                slope_rs_std=signal_features["slope_rs_std"],
                slope_rs_min=signal_features["slope_rs_min"],
                slope_rs_max=signal_features["slope_rs_max"],
                
                # Heart Rate Statistics
                heart_rate_bpm_mean=signal_features["heart_rate_bpm_mean"],
                heart_rate_bpm_std=signal_features["heart_rate_bpm_std"],
                heart_rate_bpm_min=signal_features["heart_rate_bpm_min"],
                heart_rate_bpm_max=signal_features["heart_rate_bpm_max"],
                
                # Local RMSSD Statistics
                local_rmssd_mean=signal_features["local_rmssd_mean"],
                local_rmssd_std=signal_features["local_rmssd_std"],
                local_rmssd_min=signal_features["local_rmssd_min"],
                local_rmssd_max=signal_features["local_rmssd_max"],
                
                # T Inversion Statistics
                t_inversion_sum=signal_features["t_inversion_sum"],
                t_inversion_mean=signal_features["t_inversion_mean"],
                
                # Premature Beat Count
                premature_beat_sum=signal_features["premature_beat_sum"],
                
                # Bigeminy Count
                bigeminy_sum=signal_features["bigeminy_sum"],
                
                # Trigeminy Count
                trigeminy_sum=signal_features["trigeminy_sum"],

                # Beat Type Counts
                count_N=signal_features.get("count_N", 0),
                count_L=signal_features.get("count_L", 0),
                count_R=signal_features.get("count_R", 0),
                count_slash=signal_features.get("count_/", 0),
                count_V=signal_features.get("count_V", 0),
                count_else=signal_features.get("count_else", 0),

                # Beat Type Ratios
                ratio_N=signal_features.get("ratio_N", 0.0),
                ratio_L=signal_features.get("ratio_L", 0.0),
                ratio_R=signal_features.get("ratio_R", 0.0),
                ratio_slash=signal_features.get("ratio_/", 0.0),
                ratio_V=signal_features.get("ratio_V", 0.0),
                ratio_else=signal_features.get("ratio_else", 0.0),

                # Derived Features
                percent_T_inversion=signal_features.get("percent_T_inversion", 0.0),
                QRS_prolonged_ratio=signal_features.get("QRS_prolonged_ratio", 0.0),
                QT_prolonged_ratio=signal_features.get("QT_prolonged_ratio", 0.0),
                PVC_ratio=signal_features.get("PVC_ratio", 0.0),
                num_beats=signal_features.get("num_beats", 0),
                std_Intervalle_RR_ms=signal_features.get("std_Intervalle_RR_ms", 0.0)
            )
        print(f"[StorageAgent] 🔍 All features saved")