import mlflow
from tensorflow.keras.utils import register_keras_serializable
import tensorflow as tf
mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")
from tensorflow import keras

UNet_run_id = "27d2706d1ae144dcb1cf6dfba1cd53da"  
UNet_model = mlflow.pytorch.load_model(f"runs:/{UNet_run_id}/model")
UNet_model.eval()

print("[SegmentationAgent] UNet Model loaded successfully ✅")


@register_keras_serializable()
def weighted_binary_crossentropy(y_true, y_pred):
    weight = tf.reduce_mean(y_true) * 0.5 + 0.5
    loss = tf.keras.losses.binary_crossentropy(y_true, y_pred)
    return tf.reduce_mean(loss * weight)

TCN_run_id = "19d8012f8a7e44548b19df7220defadb"

TCN_model = mlflow.keras.load_model(f"runs:/{TCN_run_id}/model", custom_objects={
    'weighted_binary_crossentropy': weighted_binary_crossentropy
})
print("[SegmentationAgent] TCN Model loaded successfully ✅")
