from __future__ import annotations

from pymilvus import MilvusClient

from smartclinic.common.base import Settings


def create_milvus_client(settings: Settings) -> MilvusClient:
    if not settings.milvus_uri:
        raise ValueError("SMARTCLINIC_MILVUS_URI is required")
    kwargs: dict[str, str] = {"uri": settings.milvus_uri}
    if settings.milvus_token:
        kwargs["token"] = settings.milvus_token
    return MilvusClient(**kwargs)
