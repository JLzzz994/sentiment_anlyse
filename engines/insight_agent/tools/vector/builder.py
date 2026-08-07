"""
Milvus 集合 schema 与索引参数的构建器
"""
from dataclasses import fields
from typing import Any

from pymilvus import AsyncMilvusClient, DataType

from engines.contracts.evidence import Engagement

MILVUS_OUTPUT_FIELDS: list[str] = [
    "doc_id",
    "platform",
    "source_table",
    "mysql_primary_key",
    "content",
    "published_at",
    *(field.name for field in fields(Engagement)),
    "hotness_score",
]


class CollectionSchemaBuilder:
    """构建Milvus 集合的 schema 与 索引参数"""

    def __init__(self, milvus_client: AsyncMilvusClient, dense_vector_dimension: int):
        self._milvus_client: AsyncMilvusClient = milvus_client
        self._dense_vector_dimension = dense_vector_dimension

    def build_collection_schema(self) -> Any:
        """定义Milvus集合字段与混合向量列结构"""
        schema = self._milvus_client.create_schema(auto_id=False, enable_dynamic_field=False)
        schema.add_field("doc_id", DataType.VARCHAR, is_primary=True, max_length=256)
        schema.add_field("platform", DataType.VARCHAR, max_length=32)
        schema.add_field("source_table", DataType.VARCHAR, max_length=64)
        schema.add_field("mysql_primary_key", DataType.INT64)
        schema.add_field("content", DataType.VARCHAR, max_length=65535)
        schema.add_field("published_at", DataType.INT64)

        for field in fields(Engagement):
            schema.add_field(field.name, DataType.FLOAT)
        schema.add_field("hotness_score", DataType.FLOAT)
        schema.add_field(
            "dense_vector",
            DataType.FLOAT_VECTOR,
            dim=self._dense_vector_dimension
        )
        schema.add_field("sparse_vector", DataType.SPARSE_FLOAT_VECTOR)
        return schema

    def build_index_params(self) -> Any:
        """配置稠密/稀疏向量列的索引类型与度量"""
        index_params = self._milvus_client.prepare_index_params()
        index_params.add_index(
            field_name="dense_vector",
            index_type='HNSW',
            metric_type='COSINE',
            params={
                'M': 64,
                "efConstruction": 100
            }
        )
        index_params.add_index(
            field_name="sparse_vector",
            index_type="SPARSE_INVERTED_INDEX",
            metric_type="IP",
            params={"inverted_index_algo": "DAAT_MAXSCORE"},
        )
        return index_params
    