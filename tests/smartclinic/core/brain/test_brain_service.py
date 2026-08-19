from __future__ import annotations

import asyncio
from types import SimpleNamespace

import numpy as np
import pytest
from fastapi import HTTPException

from smartclinic.core.brain import brain_service
from smartclinic.core.predict_labels import BRAIN_MESSAGES


def test_brain_missing_onnx_503(monkeypatch, tmp_path):
    monkeypatch.setattr(brain_service, "_SESSION", None)
    monkeypatch.setattr(brain_service, "_INPUT_NAME", None)
    monkeypatch.setattr(brain_service, "_CLASS_LABELS", None)
    monkeypatch.setattr(brain_service, "_brain_dir", lambda: tmp_path)
    with pytest.raises(HTTPException) as exc:
        brain_service._load_session()
    assert exc.value.status_code == 503


async def _read_bytes() -> bytes:
    return b"fake-image"


def test_brain_predict_returns_index_and_english_slug(monkeypatch):
    class FakeSession:
        def run(self, _outs, _feeds):
            return [np.array([[0.1, 0.2, 0.6, 0.1]], dtype=np.float32)]

    labels = {0: "glioma", 1: "meningioma", 2: "notumor", 3: "pituitary"}
    monkeypatch.setattr(
        brain_service,
        "_load_session",
        lambda: (FakeSession(), "input", labels),
    )
    monkeypatch.setattr(
        brain_service,
        "_preprocess",
        lambda _c: np.zeros((1, 240, 240, 3), dtype=np.float32),
    )

    result = asyncio.run(
        brain_service.predict_image_class(SimpleNamespace(read=_read_bytes))
    )
    assert result.prediction == 2
    assert result.predicted_class == "notumor"
    assert result.message == BRAIN_MESSAGES[2]
    assert result.confidence == 60.0


def test_brain_unknown_index_falls_back_to_json_slug(monkeypatch):
    class FakeSession:
        def run(self, _outs, _feeds):
            return [np.array([[0.1, 0.2, 0.1, 0.1, 0.9]], dtype=np.float32)]

    labels = {0: "glioma", 1: "meningioma", 2: "notumor", 3: "pituitary", 4: "other"}
    monkeypatch.setattr(
        brain_service,
        "_load_session",
        lambda: (FakeSession(), "input", labels),
    )
    monkeypatch.setattr(
        brain_service,
        "_preprocess",
        lambda _c: np.zeros((1, 240, 240, 3), dtype=np.float32),
    )

    result = asyncio.run(
        brain_service.predict_image_class(SimpleNamespace(read=_read_bytes))
    )
    assert result.prediction == 4
    assert result.predicted_class == "other"
    assert result.message == "other"


def test_brain_class_indices_file_matches_registry():
    labels_path = brain_service._labels_path()
    if not labels_path.exists():
        pytest.skip("class_indices.json not present")
    import json

    raw = json.loads(labels_path.read_text(encoding="utf-8"))
    inverted = {int(v): k for k, v in raw.items()}
    assert inverted == BRAIN_MESSAGES
