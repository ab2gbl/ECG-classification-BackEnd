from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json
import numpy as np
import joblib
import os
import pandas as pd

class_map = {
     0 : 'N',
     1 : 'L',
     2 : 'R',
     3 : '/',
     4 : 'V',
    5:'else'
}

class BeatClassifierAgent(Agent):
    class ClassifyBeat(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                model_path = os.path.join(os.path.dirname(__file__), "models", "ecg_multi_class_model.pkl")
                model = joblib.load(model_path)
                print("[BeatClassifierAgent] Features received:")
                data = json.loads(msg.body)
                features = data["features"]
                
                # Create DataFrame and exclude beat_number from prediction
                df = pd.DataFrame(features)
                df = df.drop('beat_number', axis=1)  # Remove beat_number column
                df = df[['R_index'] + [col for col in df.columns if col != 'R_index']]
                y_pred = model.predict(df)

                # Add predictions to each dictionary in the original list
                for i, feature_dict in enumerate(features):
                    Type = class_map[int(y_pred[i])]
                    feature_dict["Type"] = Type
                
                response = Message(to="controller@localhost")
                response.body = json.dumps({
                    "features": features # Your processed signal
                })
                await self.send(response)
                print("[BeatClassifierAgent] ✅ Sent processed ECG back to controller")
                model = None

    async def setup(self):
        print(f"[{self.jid}] BeatClassifierAgent started.")
        self.add_behaviour(self.ClassifyBeat())
