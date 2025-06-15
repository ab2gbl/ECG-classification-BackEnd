import joblib
import mlflow
import sys, os

import json
import pandas as pd

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(parent_dir)

import mlflow.sklearn
import globals_vars 
mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")

model_path = 'acquisition/agents/models/normal_vs_abnormal_model.pkl'

report_path = "acquisition/agents/models/normal_vs_abnormal_classification_report.json"
pred_path = "acquisition/agents/models/normal_vs_abnormal_predictions.csv"
conf_matrix_path = "acquisition/agents/models/normal_vs_abnormal_confusion_matrix.png"
model = joblib.load(model_path)
print("Signal Normality Model loaded successfully.")


with mlflow.start_run() as run:
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        registered_model_name="Signal_Normality_Model"
    )
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            report = json.load(f)
        
        mlflow.log_metric("accuracy", report.get("accuracy", 0))
        for label in ["0", "1"]:
            if label in report:
                mlflow.log_metric(f"precision_{label}", report[label].get("precision", 0))
                mlflow.log_metric(f"recall_{label}", report[label].get("recall", 0))
                mlflow.log_metric(f"f1_{label}", report[label].get("f1-score", 0))
        
        if "macro avg" in report:
            mlflow.log_metric("macro_f1", report["macro avg"].get("f1-score", 0))
        if "weighted avg" in report:
            mlflow.log_metric("weighted_f1", report["weighted avg"].get("f1-score", 0))

        mlflow.log_artifact(report_path)

    # Log predictions CSV if it exists
    if os.path.exists(pred_path):
        mlflow.log_artifact(pred_path)

    # Log confusion matrix image if it exists
    if os.path.exists(conf_matrix_path):
        mlflow.log_artifact(conf_matrix_path)

    print("Run ID:", run.info.run_id)

globals_vars.set_signal_normality_model(run.info.run_id)
