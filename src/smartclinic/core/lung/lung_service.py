from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np

from smartclinic.common.errors import feature_unavailable_error
from smartclinic.core.lung.lung_dto import PredictLung

_MODEL = None
_SCALER = None
_MODEL_PATH = Path("models/model_predict/lung_cancer.pkl")
_SCALER_PATH = Path("models/model_normalize/lung_cancer.pkl")


def _get_artifacts():
    global _MODEL, _SCALER
    if _MODEL is not None and _SCALER is not None:
        return _MODEL, _SCALER
    if not _MODEL_PATH.exists() or not _SCALER_PATH.exists():
        raise feature_unavailable_error(
            "Lung cancer model files are missing.",
            code="MISSING_MODEL",
        )
    _MODEL = joblib.load(_MODEL_PATH)
    _SCALER = joblib.load(_SCALER_PATH)
    return _MODEL, _SCALER


def process_prediction(data: PredictLung):
    if data.Age == 0:
        return 0, "Không có khả năng bị ung thư khi tuổi là 0"

    loaded_model, scaler = _get_artifacts()
    feature_vector = [
        data.Age,
        data.Gender,
        data.Air_Pollution,
        data.Alcohol_use,
        data.OccuPational_Hazards,
        data.Genetic_Risk,
        data.chronic_Lung_Disease,
        data.Smoking,
        data.Passive_Smoker,
        data.Chest_Pain,
        data.Coughing_of_Blood,
        data.Clubbing_of_Finger_Nails,
    ]

    input_data = np.array([feature_vector])
    input_data_scaled = scaler.transform(input_data)
    y_pred = loaded_model.predict(input_data_scaled)

    if y_pred[0] == 1:
        result = "Khả năng bị ung thư thấp"
    elif y_pred[0] == 2:
        result = "Khả năng ung thư ở mức độ vừa phải"
    elif y_pred[0] == 3:
        result = "Khả năng cao mắc bệnh ung thư"
    else:
        result = "Không rõ nguyên nhân"
    return int(y_pred[0]), result
