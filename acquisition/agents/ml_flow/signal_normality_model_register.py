import joblib
import mlflow
import sys, os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(parent_dir)

import mlflow.sklearn
import globals_vars 
mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")

model_path = 'acquisition/agents/models/normal_vs_abnormal_model.pkl'
model = joblib.load(model_path)
print("Signal Normality Model loaded successfully.")


with mlflow.start_run() as run:
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        registered_model_name="Signal_Normality_Model"
    )
    print("Run ID:", run.info.run_id)

globals_vars.set_signal_normality_model(run.info.run_id)
