from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json
import numpy as np
import joblib
import os
import pandas as pd
import mlflow
import globals_vars
class_map = {
     0 : 'N',
     1 : 'L',
     2 : 'R',
     3 : '/',
     4 : 'V',
    5:'else'
}

class BeatClassifierAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.Beat_classifier_model = None
        self.Beat_classifier_model_run_id =  globals_vars.get_beat_classification()

    async def setup(self):
        print(f"[{self.jid}] BeatClassifierAgent started.")
        try:
            self.Beat_classifier_model = mlflow.sklearn.load_model(f"runs:/{self.Beat_classifier_model_run_id}/model")
            
            print("[BeatClassifierAgent] Model loaded successfully ✅")

        except Exception as e:
            print(f"[BeatClassifierAgent] Error loading model: {str(e)}")
            raise

        self.add_behaviour(self.ClassifyBeat())

    class ClassifyBeat(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                try:
                    data = json.loads(msg.body)
                    features = data.get("features", [])
                    
                    # If no features, return empty response
                    if not features:
                        response = Message(to="controller@localhost")
                        response.body = json.dumps({
                            "features": [],
                            "status": "no_beats"
                        })
                        await self.send(response)
                        print("[BeatClassifierAgent] ℹ️ No beats detected, sending empty response")
                        return

                    # model_path = os.path.join(os.path.dirname(__file__), "models", "ecg_multi_class_model.pkl")
                    # model = joblib.load(model_path)
                    print("[BeatClassifierAgent] Features received:")
                    
                    # Create DataFrame and exclude beat_number from prediction
                    df = pd.DataFrame(features)
                    
                    if 'beat_number' in df.columns:
                        df = df.drop('beat_number', axis=1)  # Remove beat_number column
                    
                    if 'R_index' in df.columns:
                        df = df[['R_index'] + [col for col in df.columns if col != 'R_index']]
                    
                    y_pred = self.agent.Beat_classifier_model.predict(df)

                    # Add predictions to each dictionary in the original list
                    for i, feature_dict in enumerate(features):
                        Type = class_map[int(y_pred[i])]
                        feature_dict["Type"] = Type
                    
                    response = Message(to="controller@localhost")
                    response.body = json.dumps({
                        "features": features,
                        "status": "success"
                    })
                    await self.send(response)
                    print("[BeatClassifierAgent] ✅ Sent processed ECG back to controller")
                    
                except Exception as e:
                    print(f"[BeatClassifierAgent] ❌ Error processing beats: {str(e)}")
                    response = Message(to="controller@localhost")
                    response.body = json.dumps({
                        "features": [],
                        "status": "error",
                        "message": str(e)
                    })
                    await self.send(response)

