from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IngestedChunkText:
    """Domain chunk text produced by Docling HierarchicalChunker."""

    text: str
    headings: tuple[str, ...] = ()
