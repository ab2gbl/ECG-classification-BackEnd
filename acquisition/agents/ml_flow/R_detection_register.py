from tensorflow.keras.saving import load_model
import mlflow
import sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(parent_dir)
import globals_vars 
mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")

model_path = 'acquisition/agents/models/R_detection.h5'
model = load_model(model_path)
print("Model loaded successfully.")

with mlflow.start_run() as run:
    mlflow.keras.log_model(
        model,
        artifact_path="model",
        registered_model_name="R_detection_model"
    )
    print("Run ID:", run.info.run_id)

globals_vars.set_R_detection(run.info.run_id)
