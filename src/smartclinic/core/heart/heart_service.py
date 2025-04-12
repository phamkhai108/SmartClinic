import joblib
import numpy as np

from smartclinic.core.heart.heart_dto import PredictHeartRequestDto

model_path = r"models/model_predict/heart_failure.pkl"
loaded_model = joblib.load(model_path)


def process_prediction(data: PredictHeartRequestDto):
    feature_vector = [
        data.Age,
        data.Sex.numeric,
        data.ChestPainType.numeric,
        data.RestingBP,
        data.Cholesterol,
        data.FastingBS,
        data.RestingECG.numeric,
        data.MaxHR,
        data.ExerciseAngina.numeric,
        data.Oldpeak,
        data.ST_Slope.numeric,
    ]
    input_data = np.array([feature_vector])
    y_pred = loaded_model.predict(input_data)
    return y_pred[0]
