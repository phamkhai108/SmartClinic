from elasticsearch import Elasticsearch


def delete_documents_by_source(source_value) -> None:
    index_name = "chunks"
    es = Elasticsearch("http://localhost:9200")

    if not es.ping():
        print("Không thể kết nối tới Elasticsearch.")
        return

    query = {"query": {"term": {"source": source_value}}}

    try:
        response = es.delete_by_query(
            index=index_name, body=query, refresh=True, conflicts="proceed"
        )
        print(
            f"Đã xóa {response.get('deleted', 0)} document(s) trong index '{index_name}' với source = '{source_value}'."
        )
    except Exception as e:
        print(f"Lỗi khi xóa documents: {e}")


delete_documents_by_source("Thongbao_DangKy_DATN_2A_24_25.pdf")
