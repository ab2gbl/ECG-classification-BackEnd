from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from spade.agent import Agent
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
# Load the saved model
class DecisionAgent(Agent):
    class Decide(CyclicBehaviour):
        async def run(self):
            model_path = os.path.join(os.path.dirname(__file__), "models", "ecg_multi_class_model.pkl")
            model = joblib.load(model_path)
            msg = await self.receive(timeout=10)
            if msg:
                print("[DecisionAgent] Features received:")
                data = json.loads(msg.body)
                features = data["features"]
                #print(f"[DecisionAgent] Got features {features}")
                #print(f"[DecisionAgent] Got features {features[0]}")

                df = pd.DataFrame(features)
                df = df[['R_index'] + [col for col in df.columns if col != 'R_index']]
                y_pred = model.predict(df)


#               Add predictions to each dictionary in the original list
                for i, feature_dict in enumerate(features):
                    Type = class_map[int(y_pred[i])]
                    feature_dict["Type"] = Type
                # Extract features
                
                response = Message(to="controller@localhost")
                response.body = json.dumps({
                    "features": features # Your processed signal
                })
                await self.send(response)
                print("[FeatureAgent] ✅ Sent processed ECG back to controller")

    async def setup(self):
        print(f"[{self.jid}] DecisionAgent started.")
        self.add_behaviour(self.Decide())
