from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from asgiref.sync import sync_to_async
import json
from django.utils import timezone

from acquisition.models import Signal, SignalFeatures  # ✅ your models

class StorageAgent(Agent):
    class StoreResults(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                print("[StorageAgent] 📥 Received message to store signal")
                try:
                    data = json.loads(msg.body)
                    await self.agent.save_to_db(data)
                    print("[StorageAgent] ✅ Data saved")
                    Message(to="controller@localhost").body = "Data saved"
                    await self.send(Message(to="controller@localhost"))
                except Exception as e:
                    print(f"[StorageAgent] ❌ Error saving data: {e}")
            

    async def setup(self):
        print(f"[{self.jid}] StorageAgent ready.")
        self.add_behaviour(self.StoreResults())

    @sync_to_async
    def save_to_db(self, data):
        print("[StorageAgent] 🔧 Saving to DB...")

        signal = Signal(
            name=data["name"],
            timestamp=timezone.now()
        )
        signal.set_normalized_signal(data["normalized_signal"])
        signal.set_mask(data["full_prediction"])
        signal.save()

        print(f"[StorageAgent] 🔍 Saving feature")
        for feature in data.get("features", []):
            
            SignalFeatures.objects.create(
                        signal_name=signal,
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
        print(f"[StorageAgent] 🔍 Features saved")