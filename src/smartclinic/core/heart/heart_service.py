# Đường dẫn tới file mô hình đã lưu
import joblib
import numpy as np

from smartclinic.core.heart.heart_dto import PredictData

model_path = r'models/model_predict/heart_failure.pkl'
loaded_model = joblib.load(model_path)


def process_prediction(data: PredictData):
    feature_vector = [
        data.Age,
        data.Sex.name,
        data.ChestPainType.value,
        data.RestingBP,
        data.Cholesterol,
        data.FastingBS,
        data.RestingECG.value,
        data.MaxHR,
        data.ExerciseAngina.value,
        data.Oldpeak,
        data.ST_Slope.value
    ]
    input_data = np.array([feature_vector])
    y_pred = loaded_model.predict(input_data)
    return y_pred[0]