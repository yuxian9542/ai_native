"""
Elasticsearch索引定义
"""

# Excel元数据索引的Mapping定义
EXCEL_METADATA_INDEX = "excel_metadata"

EXCEL_METADATA_MAPPING = {
    "mappings": {
        "properties": {
            "file_id": {
                "type": "keyword"
            },
            "file_name": {
                "type": "text",
                "analyzer": "ik_max_word",
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "file_path": {
                "type": "keyword"
            },
            "processed_path": {
                "type": "keyword"
            },
            "summary": {
                "type": "text",
                "analyzer": "ik_smart"
            },
            "columns": {
                "type": "nested",
                "properties": {
                    "name": {
                        "type": "text",
                        "analyzer": "ik_max_word"
                    },
                    "type": {
                        "type": "keyword"
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "ik_smart"
                    },
                    "sample_values": {
                        "type": "keyword"
                    },
                    "unique_count": {
                        "type": "integer"
                    },
                    "null_count": {
                        "type": "integer"
                    }
                }
            },
            "embedding": {
                "type": "dense_vector",
                "dims": 1536,
                "similarity": "cosine"
            },
            "tags": {
                "type": "keyword"
            },
            "created_at": {
                "type": "date"
            },
            "updated_at": {
                "type": "date"
            }
        }
    },
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    }
}

