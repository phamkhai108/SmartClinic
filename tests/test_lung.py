from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException

from smartclinic.core.lung import lung_service
from smartclinic.core.lung.lung_dto import PredictLung

SAMPLE = PredictLung(
    Age=50,
    Gender=1,
    Air_Pollution=3,
    Alcohol_use=2,
    OccuPational_Hazards=2,
    Genetic_Risk=2,
    chronic_Lung_Disease=2,
    Smoking=3,
    Passive_Smoker=2,
    Chest_Pain=3,
    Coughing_of_Blood=2,
    Clubbing_of_Finger_Nails=2,
)


def test_lung_age_zero_short_circuits():
    pred, msg = lung_service.process_prediction(SAMPLE.model_copy(update={"Age": 0}))
    assert pred == 0
    assert msg


def test_lung_missing_model_503(monkeypatch, tmp_path):
    monkeypatch.setattr(lung_service, "_MODEL", None)
    monkeypatch.setattr(lung_service, "_SCALER", None)
    monkeypatch.setattr(lung_service, "_MODEL_PATH", tmp_path / "missing.pkl")
    monkeypatch.setattr(lung_service, "_SCALER_PATH", tmp_path / "missing_scaler.pkl")
    with pytest.raises(HTTPException) as exc:
        lung_service.process_prediction(SAMPLE)
    assert exc.value.status_code == 503


def test_lung_predict_with_real_model():
    model = Path("models/model_predict/lung_cancer.pkl")
    scaler = Path("models/model_normalize/lung_cancer.pkl")
    if not model.exists() or not scaler.exists():
        pytest.skip("model artifacts not present")
    lung_service._MODEL = None
    lung_service._SCALER = None
    pred, _msg = lung_service.process_prediction(SAMPLE)
    assert pred in (1, 2, 3)
