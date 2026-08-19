from __future__ import annotations

import asyncio
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from smartclinic.api.deps_auth import CurrentUser
from smartclinic.api.routers import brain as brain_router
from smartclinic.api.routers import breast as breast_router
from smartclinic.api.routers import heart as heart_router
from smartclinic.api.routers import lung as lung_router
from smartclinic.core.brain.brain_dto import PredictBrainResponse
from smartclinic.core.breast_cancer.breast_dto import PredictBreastRequest
from smartclinic.core.heart.heart_dto import (
    ChestPainTypeEnum,
    ExerciseAnginaEnum,
    PredictHeartRequestDto,
    RestingECGEnum,
    SexEnum,
    STSlopeEnum,
)
from smartclinic.core.lung.lung_dto import PredictLung
from smartclinic.core.predict_labels import get_english_message

USER = CurrentUser(id="u1", user_name="tester", email="t@example.com", role="doctor")

HEART_SAMPLE = PredictHeartRequestDto(
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

LUNG_SAMPLE = PredictLung(
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

BREAST_SAMPLE = PredictBreastRequest.model_validate(
    {
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
)


def test_heart_router_returns_english_message(monkeypatch, caplog):
    monkeypatch.setattr(heart_router, "process_prediction", lambda _data: 1)
    with caplog.at_level(logging.INFO):
        resp = heart_router.predict(HEART_SAMPLE, USER)
    assert resp.prediction == 1
    assert resp.message == get_english_message("heart", 1)
    assert "predict.heart" in caplog.text
    assert "prediction=1" in caplog.text


def test_heart_router_class_zero(monkeypatch):
    monkeypatch.setattr(heart_router, "process_prediction", lambda _data: 0)
    resp = heart_router.predict(HEART_SAMPLE, USER)
    assert resp.message == "No heart failure symptoms"


def test_heart_router_reraises_http_exception(monkeypatch):
    def _boom(_data):
        raise HTTPException(status_code=503, detail="missing")

    monkeypatch.setattr(heart_router, "process_prediction", _boom)
    with pytest.raises(HTTPException) as exc:
        heart_router.predict(HEART_SAMPLE, USER)
    assert exc.value.status_code == 503


def test_heart_router_wraps_unexpected_errors(monkeypatch):
    monkeypatch.setattr(
        heart_router,
        "process_prediction",
        lambda _data: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    with pytest.raises(HTTPException) as exc:
        heart_router.predict(HEART_SAMPLE, USER)
    assert exc.value.status_code == 500


def test_lung_router_returns_english_message(monkeypatch, caplog):
    monkeypatch.setattr(lung_router, "process_prediction", lambda _data: 3)
    with caplog.at_level(logging.INFO):
        resp = lung_router.predict(LUNG_SAMPLE, USER)
    assert resp.prediction == 3
    assert resp.message == "High cancer risk"
    assert "predict.lung" in caplog.text


def test_lung_router_age_zero_message(monkeypatch):
    monkeypatch.setattr(lung_router, "process_prediction", lambda _data: 0)
    resp = lung_router.predict(LUNG_SAMPLE, USER)
    assert resp.prediction == 0
    assert resp.message == "No cancer risk when age is 0"


def test_lung_router_unknown_class_message(monkeypatch):
    monkeypatch.setattr(lung_router, "process_prediction", lambda _data: 9)
    resp = lung_router.predict(LUNG_SAMPLE, USER)
    assert resp.message == "Unknown class 9"


def test_lung_router_wraps_unexpected_errors(monkeypatch):
    monkeypatch.setattr(
        lung_router,
        "process_prediction",
        lambda _data: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    with pytest.raises(HTTPException) as exc:
        lung_router.predict(LUNG_SAMPLE, USER)
    assert exc.value.status_code == 500


def test_breast_router_returns_english_message(monkeypatch, caplog):
    monkeypatch.setattr(breast_router, "process_prediction", lambda _data: 1)
    with caplog.at_level(logging.INFO):
        resp = breast_router.predict(BREAST_SAMPLE, USER)
    assert resp.prediction == 1
    assert resp.message == "Malignant"
    assert "predict.breast" in caplog.text


def test_breast_router_benign(monkeypatch):
    monkeypatch.setattr(breast_router, "process_prediction", lambda _data: 0)
    resp = breast_router.predict(BREAST_SAMPLE, USER)
    assert resp.message == "Benign"


def test_breast_router_wraps_unexpected_errors(monkeypatch):
    monkeypatch.setattr(
        breast_router,
        "process_prediction",
        lambda _data: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    with pytest.raises(HTTPException) as exc:
        breast_router.predict(BREAST_SAMPLE, USER)
    assert exc.value.status_code == 500


def test_lung_router_reraises_http_exception(monkeypatch):
    def _boom(_data):
        raise HTTPException(status_code=503, detail="missing")

    monkeypatch.setattr(lung_router, "process_prediction", _boom)
    with pytest.raises(HTTPException) as exc:
        lung_router.predict(LUNG_SAMPLE, USER)
    assert exc.value.status_code == 503


def test_breast_router_reraises_http_exception(monkeypatch):
    def _boom(_data):
        raise HTTPException(status_code=503, detail="missing")

    monkeypatch.setattr(breast_router, "process_prediction", _boom)
    with pytest.raises(HTTPException) as exc:
        breast_router.predict(BREAST_SAMPLE, USER)
    assert exc.value.status_code == 503


def test_brain_router_returns_prediction_and_logs(monkeypatch, caplog):
    payload = PredictBrainResponse(
        prediction=0,
        predicted_class="glioma",
        confidence=91.2,
        message="glioma",
    )
    monkeypatch.setattr(
        brain_router, "predict_image_class", AsyncMock(return_value=payload)
    )
    file = SimpleNamespace(filename="scan.jpg")
    with caplog.at_level(logging.INFO):
        result = asyncio.run(brain_router.predict(USER, file))
    assert result.prediction == 0
    assert result.message == "glioma"
    assert "predict.brain" in caplog.text


def test_brain_router_rejects_non_image():
    file = SimpleNamespace(filename="notes.txt")
    with pytest.raises(HTTPException) as exc:
        asyncio.run(brain_router.predict(USER, file))
    assert exc.value.status_code == 400


def test_brain_router_rejects_missing_filename():
    file = SimpleNamespace(filename=None)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(brain_router.predict(USER, file))
    assert exc.value.status_code == 400


def test_brain_router_wraps_unexpected_errors(monkeypatch):
    monkeypatch.setattr(
        brain_router,
        "predict_image_class",
        AsyncMock(side_effect=RuntimeError("onnx down")),
    )
    file = SimpleNamespace(filename="scan.png")
    with pytest.raises(HTTPException) as exc:
        asyncio.run(brain_router.predict(USER, file))
    assert exc.value.status_code == 500


def test_brain_router_reraises_http_exception(monkeypatch):
    monkeypatch.setattr(
        brain_router,
        "predict_image_class",
        AsyncMock(side_effect=HTTPException(status_code=503, detail="missing")),
    )
    file = SimpleNamespace(filename="scan.jpg")
    with pytest.raises(HTTPException) as exc:
        asyncio.run(brain_router.predict(USER, file))
    assert exc.value.status_code == 503


def test_predict_endpoint_docstrings_document_classes():
    assert "0" in heart_router.predict.__doc__
    assert "heart failure" in heart_router.predict.__doc__
    assert "low cancer risk" in lung_router.predict.__doc__
    assert "malignant" in breast_router.predict.__doc__
    assert "glioma" in brain_router.predict.__doc__
    assert "i18n" in heart_router.predict.__doc__
