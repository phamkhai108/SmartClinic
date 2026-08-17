from __future__ import annotations

from unittest.mock import MagicMock

from smartclinic.core.search.search_service import search_vector_cosine


def test_search_vector_cosine_embeds_then_searches():
    repo = MagicMock()
    repo.search_cosine.return_value = "result"
    embed = MagicMock()
    embed.embed.return_value = [0.1, 0.2]
    out = search_vector_cosine(repo, embed, "query", size=3)
    embed.embed.assert_called_once_with("query")
    repo.search_cosine.assert_called_once_with([0.1, 0.2], 3)
    assert out == "result"
