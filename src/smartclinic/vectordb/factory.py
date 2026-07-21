from __future__ import annotations

from smartclinic.common.base import Settings
from smartclinic.common.errors import feature_unavailable_error, missing_config_error
from smartclinic.vectordb.constants import VectorBackend
from smartclinic.vectordb.elasticsearch.es_service import ElasticsearchChunkRepository
from smartclinic.vectordb.milvus.milvus_client import create_milvus_client
from smartclinic.vectordb.milvus.milvus_service import MilvusChunkRepository
from smartclinic.vectordb.protocols import ChunkRepository


def build_chunk_repository(settings: Settings) -> ChunkRepository:
    backend: VectorBackend = settings.vector_backend
    if backend == "elasticsearch":
        if not settings.es_host:
            raise missing_config_error(["SMARTCLINIC_ES_HOST"])
        from elasticsearch import Elasticsearch

        try:
            client = Elasticsearch(
                hosts=settings.es_host,
                request_timeout=30,
                max_retries=2,
            )
        except Exception as exc:
            raise feature_unavailable_error(
                f"Elasticsearch unavailable: {exc}",
            ) from exc
        return ElasticsearchChunkRepository(client)

    if backend == "milvus":
        if not settings.milvus_uri:
            raise missing_config_error(["SMARTCLINIC_MILVUS_URI"])
        try:
            client = create_milvus_client(settings)
        except Exception as exc:
            raise feature_unavailable_error(
                f"Milvus unavailable: {exc}",
            ) from exc
        return MilvusChunkRepository(client)

    raise missing_config_error(["SMARTCLINIC_VECTOR_BACKEND"])
