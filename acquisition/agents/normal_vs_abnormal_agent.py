from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import pandas as pd
from collections import Counter
import json
import joblib , os
import mlflow.sklearn
import globals_vars
def flatten_feature_dict(d, keep_sums_for=None, keep_means_for=None):
    if keep_sums_for is None:
        keep_sums_for = {'T_inversion', 'Premature_beat', 'Bigeminy', 'Trigeminy'}
    if keep_means_for is None:
        keep_means_for = {'T_inversion', 'Premature_beat', 'Bigeminy', 'Trigeminy'}

    flat = {}
    for k, v in d.items():
        if isinstance(v, dict):
            for subk, subv in v.items():
                if pd.isna(subv):
                    continue  # Skip NaNs entirely
                # Always keep mean values
                if subk == 'mean':
                    flat[f'{k}_{subk}'] = subv
                # Keep sum only for specified features
                elif subk == 'sum' and k in keep_sums_for:
                    flat[f'{k}_{subk}'] = subv
                # Keep min, max, std for non-binary columns
                elif subk in {'min', 'max', 'std'} and k not in keep_sums_for:
                    flat[f'{k}_{subk}'] = subv
        else:
            if not pd.isna(v):
                flat[k] = v
    return flat


def standardize_feature_keys(features):
    """Standardize feature keys by converting to lowercase and fixing ratio names."""
    standardized = {}
    for key, value in features.items():
        # Convert key to lowercase
        new_key = key.lower()
        # Fix specific ratio names
        if new_key == "t/r_ratio" or new_key == "t/r_ratio_mean" or new_key == "t/r_ratio_min" or new_key == "t/r_ratio_max" or new_key == "t/r_ratio_std":
            new_key = new_key.replace("t/r_ratio", "t_r_ratio")
        elif new_key == "p/r_ratio" or new_key == "p/r_ratio_mean" or new_key == "p/r_ratio_min" or new_key == "p/r_ratio_max" or new_key == "p/r_ratio_std":
            new_key = new_key.replace("p/r_ratio", "p_r_ratio")
        standardized[new_key] = value
    return standardized

def extract_signal_features(df_signal):
    # Aggregation
    agg_funcs = {
        'Duree_QRS_ms': ['mean', 'std', 'min', 'max'],
        'Duree_P_ms': ['mean', 'std', 'min', 'max'],
        'Duree_T_ms': ['mean', 'std', 'min', 'max'],
        'Intervalle_QT_ms': ['mean', 'std', 'min', 'max'],
        'Intervalle_PR_ms': ['mean', 'std', 'min', 'max'],
        'Intervalle_ST_ms': ['mean', 'std', 'min', 'max'],
        'Amplitude_P': ['mean', 'std', 'min', 'max'],
        'Amplitude_Q': ['mean', 'std', 'min', 'max'],
        'Amplitude_R': ['mean', 'std', 'min', 'max'],
        'Amplitude_S': ['mean', 'std', 'min', 'max'],
        'Amplitude_T': ['mean', 'std', 'min', 'max'],
        'T/R_ratio': ['mean', 'std', 'min', 'max'],
        'P/R_ratio': ['mean', 'std', 'min', 'max'],
        'QRS_area': ['mean', 'std', 'min', 'max'],
        'Slope_QR': ['mean', 'std', 'min', 'max'],
        'Slope_RS': ['mean', 'std', 'min', 'max'],
        'Heart_rate_bpm': ['mean', 'std', 'min', 'max'],
        'Local_RMSSD': ['mean', 'std', 'min', 'max'],
        'T_inversion': ['sum', 'mean'],
        'Premature_beat': ['sum'],
        'Bigeminy': ['sum'],
        'Trigeminy': ['sum'],
    }

    agg_df = df_signal.agg(agg_funcs)
    agg_df.columns = [''.join(col).strip() for col in agg_df.columns.values]
    agg_features = agg_df.to_dict()

    beat_types = df_signal['Type'].tolist()
    type_counts = Counter(beat_types)
    total_beats = len(df_signal)

    type_features = {
        f'count_{t}': type_counts.get(t, 0)
        for t in ['N', 'L', 'R', '/', 'V', 'else']
    }
    type_features.update({
        f'ratio_{t}': type_counts.get(t, 0) / total_beats if total_beats > 0 else 0
        for t in ['N', 'L', 'R', '/', 'V', 'else']
    })

    derived_features = {
        'percent_T_inversion': df_signal['T_inversion'].mean(),
        'QRS_prolonged_ratio': (df_signal['Duree_QRS_ms'] > 120).mean(),
        'QT_prolonged_ratio': (df_signal['Intervalle_QT_ms'] > 450).mean(),
        'PVC_ratio': type_counts.get('V', 0) / total_beats if total_beats > 0 else 0,
        'num_beats': total_beats,
        'std_Intervalle_RR_ms': df_signal['Intervalle_RR_ms'].std(skipna=True)
    }

    signal_features = {
        **agg_features,
        **type_features,
        **derived_features
    }

    
    # Then standardize the keys
    return flatten_feature_dict(signal_features)

class NormalVsAbnormalAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.model = None
        self.model_run_id =  globals_vars.get_signal_normality_model()


    async def setup(self):
        print(f"[{self.jid}] NormalVsAbnormalAgent ready.")
        try:
            self.model = mlflow.sklearn.load_model(f"runs:/{self.model_run_id}/model")
            
            print("[NormalVsAbnormalAgent] Model loaded successfully ✅")

        except Exception as e:
            print(f"[NormalVsAbnormalAgent] Error loading model: {str(e)}")
            raise

        self.add_behaviour(self.ClassifySignal()) 
    class ClassifySignal(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                print("[NormalVsAbnormalAgent] 📥 Received signal features for classification")
                try:
                    data = json.loads(msg.body)
                    beat_features = data.get("features", [])
                    print("[NormalVsAbnormalAgent] got features:", len(beat_features))
                    
                    beat_features = pd.DataFrame(beat_features)
                    signal_features = extract_signal_features(beat_features)
                    
                    
                    df = pd.DataFrame([signal_features])
                    y_pred = self.agent.model.predict(df)
                    y_pred = y_pred[0]
                    
                    # Classify as Normal (0) or Abnormal (1)
                    if y_pred == 0:
                        signal_type = "Normal"
                    else:
                        signal_type = "Abnormal"
                    
                    signal_features = standardize_feature_keys(signal_features)
                    
                    # Send response to controller
                    response = Message(to="controller@localhost")
                    response.body = json.dumps({
                        "signal_features": signal_features,
                        "signal_type": signal_type
                    })
                    await self.send(response)
                    print("[NormalVsAbnormalAgent] ✅ Sent classified features to controller")
                except Exception as e:
                    print(f"[NormalVsAbnormalAgent] ❌ Error processing features: {e}")
