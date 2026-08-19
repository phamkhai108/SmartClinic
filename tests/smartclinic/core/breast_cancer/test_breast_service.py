from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest
from fastapi import HTTPException

from smartclinic.core.breast_cancer import breast_service
from smartclinic.core.breast_cancer.breast_dto import PredictBreastRequest

SAMPLE = {
    "radius_mean": 17.99,
    "texture_mean": 10.38,
    "perimeter_mean": 122.8,
    "area_mean": 1001.0,
    "smoothness_mean": 0.1184,
    "compactness_mean": 0.2776,
    "concavity_mean": 0.3001,
    "concave points_mean": 0.1471,
    "radius_se": 1.095,
    "perimeter_se": 8.589,
    "area_se": 153.4,
    "concavity_se": 0.05373,
    "radius_worst": 25.38,
    "texture_worst": 17.33,
    "perimeter_worst": 184.6,
    "area_worst": 2019.0,
    "smoothness_worst": 0.1622,
    "compactness_worst": 0.6656,
    "concavity_worst": 0.7119,
    "concave points_worst": 0.2654,
    "symmetry_worst": 0.4601,
}


def test_breast_predict_returns_int_class(monkeypatch):
    model = MagicMock()
    model.predict.return_value = np.array([1])
    scaler = MagicMock()
    scaler.transform.side_effect = lambda x: x
    monkeypatch.setattr(breast_service, "_get_artifacts", lambda: (model, scaler))
    pred = breast_service.process_prediction(PredictBreastRequest.model_validate(SAMPLE))
    assert pred == 1
    assert isinstance(pred, int)


def test_breast_missing_model_503(monkeypatch, tmp_path):
    monkeypatch.setattr(breast_service, "_MODEL", None)
    monkeypatch.setattr(breast_service, "_SCALER", None)
    monkeypatch.setattr(breast_service, "_MODEL_PATH", tmp_path / "missing.pkl")
    monkeypatch.setattr(breast_service, "_SCALER_PATH", tmp_path / "missing_scaler.pkl")
    with pytest.raises(HTTPException) as exc:
        breast_service.process_prediction(PredictBreastRequest.model_validate(SAMPLE))
    assert exc.value.status_code == 503


def test_breast_predict_with_real_model():
    if not Path("models/model_predict/breast_cancer.pkl").exists():
        pytest.skip("model artifacts not present")
    breast_service._MODEL = None
    breast_service._SCALER = None
    pred = breast_service.process_prediction(PredictBreastRequest.model_validate(SAMPLE))
    assert pred in (0, 1)
    assert isinstance(pred, int)
