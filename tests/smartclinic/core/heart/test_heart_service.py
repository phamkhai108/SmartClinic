from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException

from smartclinic.core.heart import heart_service
from smartclinic.core.heart.heart_dto import (
    ChestPainTypeEnum,
    ExerciseAnginaEnum,
    PredictHeartRequestDto,
    RestingECGEnum,
    SexEnum,
    STSlopeEnum,
)

SAMPLE = PredictHeartRequestDto(
    Age=55,
    Sex=SexEnum.M,
    ChestPainType=ChestPainTypeEnum.ASY,
    RestingBP=140,
    Cholesterol=250,
    FastingBS=0,
    RestingECG=RestingECGEnum.Normal,
    MaxHR=150,
    ExerciseAngina=ExerciseAnginaEnum.N,
    Oldpeak=1.0,
    ST_Slope=STSlopeEnum.Flat,
)


def test_heart_missing_model_503(monkeypatch, tmp_path):
    monkeypatch.setattr(heart_service, "_MODEL", None)
    monkeypatch.setattr(heart_service, "_MODEL_PATH", tmp_path / "missing.pkl")
    with pytest.raises(HTTPException) as exc:
        heart_service.process_prediction(SAMPLE)
    assert exc.value.status_code == 503


def test_heart_predict_with_real_model():
    if not Path("models/model_predict/heart_failure.pkl").exists():
        pytest.skip("model artifacts not present")
    heart_service._MODEL = None
    pred = heart_service.process_prediction(SAMPLE)
    assert int(pred) in (0, 1)
