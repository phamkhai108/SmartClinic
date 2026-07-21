from pathlib import Path

import joblib
import numpy as np

from smartclinic.common.errors import feature_unavailable_error
from smartclinic.core.breast_cancer.breast_dto import PredictBreastRequest

_MODEL = None
_SCALER = None
_MODEL_PATH = Path("models/model_predict/breast_cancer.pkl")
_SCALER_PATH = Path("models/model_normalize/breast_cancer.pkl")

FEATURE_ORDER = [
    "radius_mean",
    "texture_mean",
    "perimeter_mean",
    "area_mean",
    "smoothness_mean",
    "compactness_mean",
    "concavity_mean",
    "concave points_mean",
    "radius_se",
    "perimeter_se",
    "area_se",
    "concavity_se",
    "radius_worst",
    "texture_worst",
    "perimeter_worst",
    "area_worst",
    "smoothness_worst",
    "compactness_worst",
    "concavity_worst",
    "concave points_worst",
    "symmetry_worst",
]


def _get_artifacts():
    global _MODEL, _SCALER
    if _MODEL is not None and _SCALER is not None:
        return _MODEL, _SCALER
    if not _MODEL_PATH.exists() or not _SCALER_PATH.exists():
        raise feature_unavailable_error(
            "Breast cancer model files are missing.",
            code="MISSING_MODEL",
        )
    _MODEL = joblib.load(_MODEL_PATH)
    _SCALER = joblib.load(_SCALER_PATH)
    return _MODEL, _SCALER


def process_prediction(data: PredictBreastRequest) -> tuple[int, str]:
    model, scaler = _get_artifacts()
    raw = data.model_dump(by_alias=True)
    vector = [raw[name] for name in FEATURE_ORDER]
    scaled = scaler.transform(np.array([vector]))
    pred = int(model.predict(scaled)[0])
    if pred == 1:
        return pred, "Khả năng ác tính (Malignant)"
    return pred, "Khả năng lành tính (Benign)"
