from elasticsearch import Elasticsearch

from smartclinic.common.base import AppConfig


def get_elasticsearch_client() -> Elasticsearch:
    return Elasticsearch(hosts=AppConfig.es_host, request_timeout=30, max_retries=2)
