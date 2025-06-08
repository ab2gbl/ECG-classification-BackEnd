import os
import mlflow
import mlflow.sklearn
import joblib
import json
import pandas as pd

import sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(parent_dir)
import globals_vars 

# Set this if needed
mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")

# Paths
model_path = "acquisition/agents/models/others/sinus arrhythmia_vs_else_model.pkl"
report_path = "acquisition/agents/models/others/sinus_arrhythmia_classification_report.json"
pred_path = "acquisition/agents/models/others/sinus_arrhythmia_predictions.csv"
conf_matrix_path = "acquisition/agents/models/others/sinus_arrhythmia_confusion_matrix.png"

# Load model (required)
model = joblib.load(model_path)

with mlflow.start_run() as run:
    # Always log model
    mlflow.sklearn.log_model(model, "model", registered_model_name="sinus_arrhythmia_Model")

    # Log metrics if report exists
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

    print("sinus_arrhythmia_Model logged. Optional files were uploaded if found.")



globals_vars.set_signal_sinus_arrhythmia_model(run.info.run_id)