from __future__ import annotations

from datetime import datetime

from smartclinic.vectordb.milvus.milvus_service import (
    _escape_filter_value,
    _parse_datetime,
)


def test_escape_filter_value_quotes_and_backslashes():
    assert _escape_filter_value('a"b\\c') == 'a\\"b\\\\c'


def test_parse_datetime_passthrough_and_isoformat():
    now = datetime(2024, 1, 2, 3, 4, 5)
    assert _parse_datetime(now) is now
    assert _parse_datetime("2024-01-02T03:04:05") == now
