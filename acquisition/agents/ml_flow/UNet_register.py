import sys
import os

# Get the parent directory of the current file
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.append(parent_dir)

from segmentation_model import UNet1D_Enhanced
import torch
import mlflow
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(parent_dir)
import globals_vars 
mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")

print("loading UNet model...")
device = torch.device("cuda" if torch.cuda.is_available(    ) else "cpu")

model_path = 'acquisition/agents/models/unet1d_ecg_qrs.pth'
model = UNet1D_Enhanced(n_classes=4).to(device)
model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()
print("Model loaded successfully.")

signature = mlflow.models.infer_signature(
    model_input=torch.randn(1, 1, 240),  # Example input tensor
    model_output=torch.randn(1, 4, 240)  # Example output tensor
)


with mlflow.start_run() as run:
    #mlflow.pytorch.log_model(model, "model", signature=signature)
    #mlflow.pytorch.log_model(model, "model", registered_model_name="UNet_segmenatation_v1")
    mlflow.pytorch.log_model(
        model, 
        "model",
        registered_model_name="UNet_segmenatation",
        signature=signature,
        #input_example={"input": torch.randn(1, 1, 240)}  # Example input for signature inference
    )
    print("Run ID:", run.info.run_id)

globals_vars.set_UNet(run.info.run_id)
'''
Model loaded successfully.
2025/06/01 10:08:34 WARNING mlflow.models.signature: Failed to infer schema for inputs. Setting schema to `Schema([ColSpec(type=AnyType())]` as default. Note that MLflow doesn't validate data types during inference for AnyType. To see the full traceback, set logging level to DEBUG.
2025/06/01 10:08:34 WARNING mlflow.models.signature: Failed to infer schema for outputs. Setting schema to `Schema([ColSpec(type=AnyType())]` as default. To see the full traceback, set logging level to DEBUG.
Registered model 'UNet_segmenatation_v1' already exists. Creating a new version of this model...
2025/06/01 10:08:58 INFO mlflow.store.model_registry.abstract_store: Waiting up to 300 seconds for model version to finish creation. Model name: UNet_segmenatation_v1, version 3
Created version '3' of model 'UNet_segmenatation_v1'.
Run ID: 27d2706d1ae144dcb1cf6dfba1cd53da
🏃 View run learned-foal-399 at: http://127.0.0.1:8080/#/experiments/0/runs/27d2706d1ae144dcb1cf6dfba1cd53da
🧪 View experiment at: http://127.0.0.1:8080/#/experiments/0

'''