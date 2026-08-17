from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from smartclinic.core.llm.llm_service import LLMModel


def _model_with_client(client) -> LLMModel:
    model = LLMModel.__new__(LLMModel)
    model.model_id = "emb"
    model.client = client
    return model


def test_embed_many_empty():
    model = _model_with_client(MagicMock())
    assert model.embed_many([]) == []


def test_embed_many_batch_path():
    client = MagicMock()
    client.embeddings.create.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(index=1, embedding=[0.2]),
            SimpleNamespace(index=0, embedding=[0.1]),
        ]
    )
    model = _model_with_client(client)
    assert model.embed_many(["a", "b"]) == [[0.1], [0.2]]
    client.embeddings.create.assert_called_once()


def test_embed_many_falls_back_to_per_item():
    client = MagicMock()
    client.embeddings.create.side_effect = [
        RuntimeError("list rejected"),
        SimpleNamespace(data=[SimpleNamespace(index=0, embedding=[1.0])]),
        SimpleNamespace(data=[SimpleNamespace(index=0, embedding=[2.0])]),
    ]
    model = _model_with_client(client)
    assert model.embed_many(["a", "b"]) == [[1.0], [2.0]]
    assert client.embeddings.create.call_count == 3


def test_embed_many_raises_on_count_mismatch():
    client = MagicMock()
    client.embeddings.create.return_value = SimpleNamespace(
        data=[SimpleNamespace(index=0, embedding=[0.1])]
    )
    model = _model_with_client(client)
    with pytest.raises(RuntimeError, match="count mismatch"):
        model.embed_many(["a", "b"])


def test_embed_delegates_to_embed_many():
    client = MagicMock()
    client.embeddings.create.return_value = SimpleNamespace(
        data=[SimpleNamespace(index=0, embedding=[9.0])]
    )
    model = _model_with_client(client)
    assert model.embed("x") == [9.0]
