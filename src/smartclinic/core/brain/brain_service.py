import io
import json

import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

from smartclinic.core.brain.brain_dto import PredictResponse

# Load model & class indices once
model = load_model("models/model_predict/brain/Tumor_classification_vgg16.h5")

with open("models/model_predict/brain/class_indices.json", "r") as f:
    class_indices = json.load(f)

# Đảo ngược class_indices
class_labels = {v: k for k, v in class_indices.items()}

async def predict_image_class(file) -> dict:
    # Đọc ảnh từ UploadFile
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    img = img.resize((240, 240))
    
    # Tiền xử lý ảnh
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Dự đoán
    predictions = model.predict(img_array)
    predicted_class_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_class_idx])

    # return {
    #     "predicted_class": class_labels[predicted_class_idx],
    #     "confidence": round(confidence * 100, 2)
    # }
    return PredictResponse(
        predicted_class=class_labels[predicted_class_idx],
        confidence=round(confidence * 100, 2)

    )
