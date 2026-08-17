from __future__ import annotations

import pytest
from fastapi import HTTPException

from smartclinic.core.brain import brain_service


def test_brain_missing_onnx_503(monkeypatch, tmp_path):
    monkeypatch.setattr(brain_service, "_SESSION", None)
    monkeypatch.setattr(brain_service, "_INPUT_NAME", None)
    monkeypatch.setattr(brain_service, "_CLASS_LABELS", None)
    monkeypatch.setattr(brain_service, "_brain_dir", lambda: tmp_path)
    with pytest.raises(HTTPException) as exc:
        brain_service._load_session()
    assert exc.value.status_code == 503
