from __future__ import annotations

from smartclinic.common.errors import feature_unavailable_error, missing_config_error


def test_missing_config_error_shape():
    exc = missing_config_error(["SMARTCLINIC_ES_HOST"])
    assert exc.status_code == 503
    assert exc.detail["code"] == "MISSING_CONFIG"
    assert exc.detail["keys"] == ["SMARTCLINIC_ES_HOST"]


def test_feature_unavailable_error_shape():
    exc = feature_unavailable_error("down", code="ES_DOWN")
    assert exc.status_code == 503
    assert exc.detail == {"code": "ES_DOWN", "message": "down", "keys": []}
