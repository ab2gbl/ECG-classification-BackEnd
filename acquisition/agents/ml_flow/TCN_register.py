from tensorflow.keras.utils import register_keras_serializable
from keras.saving import load_model
import tensorflow as tf
import mlflow
import sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(parent_dir)
import globals_vars 
mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")

@register_keras_serializable()
def weighted_binary_crossentropy(y_true, y_pred):
    weight = tf.reduce_mean(y_true) * 0.5 + 0.5
    loss = tf.keras.losses.binary_crossentropy(y_true, y_pred)
    return tf.reduce_mean(loss * weight)

model_path = 'acquisition/agents/models/TCN.keras'
model = load_model(model_path, custom_objects={
                        'weighted_binary_crossentropy': weighted_binary_crossentropy
                    })
print("Model loaded successfully.")

with mlflow.start_run() as run:
    mlflow.keras.log_model(
        model,
        artifact_path="model",
        registered_model_name="TCN_segmenatation"
    )
    print("Run ID:", run.info.run_id)

globals_vars.set_TCN(run.info.run_id)

'''
Successfully registered model 'QRS_TCN_Model'.
2025/06/01 10:34:09 INFO mlflow.store.model_registry.abstract_store: Waiting up to 300 seconds for model version to finish creation. Model name: QRS_TCN_Model, version 1
Created version '1' of model 'QRS_TCN_Model'.
Run ID: 19d8012f8a7e44548b19df7220defadb
🏃 View run magnificent-gnu-125 at: http://127.0.0.1:8080/#/experiments/0/runs/19d8012f8a7e44548b19df7220defadb
🧪 View experiment at: http://127.0.0.1:8080/#/experiments/0
'''