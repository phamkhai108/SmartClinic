from pathlib import Path

import joblib
import numpy as np

from smartclinic.common.errors import feature_unavailable_error
from smartclinic.core.heart.heart_dto import PredictHeartRequestDto

_MODEL = None
_MODEL_PATH = Path("models/model_predict/heart_failure.pkl")


def _get_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    if not _MODEL_PATH.exists():
        raise feature_unavailable_error(
            "Heart failure model file is missing.",
            code="MISSING_MODEL",
        )
    _MODEL = joblib.load(_MODEL_PATH)
    return _MODEL


def process_prediction(data: PredictHeartRequestDto):
    loaded_model = _get_model()
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
