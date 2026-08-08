"""从MySQL中读取文档供向量同步"""
from dataclasses import fields
from datetime import datetime

from sqlalchemy import RowMapping

from engines.contracts.evidence import Engagement
from engines.insight_agent.tools.db_connection import DatabaseConnectionManager, database_connection_manager
from engines.insight_agent.tools.search_results import EvidenceDocument
from engines.insight_agent.tools.sql import vector_sql_statement


class DocumentRecordReader:
    def __init__(self, conn_manager: DatabaseConnectionManager = database_connection_manager):
        self._conn_manager = conn_manager

    async def read_all_documents(self) -> list[EvidenceDocument]:
        # async with self._conn_manager.get_async_session_factory() as session:
        async with self._conn_manager.get_async_engine().connect() as conn:
            result = await conn.execute(vector_sql_statement())
            rows = result.mappings().all()
            return [doc for row in rows if (doc := self._row_to_doc(row))]
    @staticmethod
    def _row_to_doc( row: RowMapping) -> EvidenceDocument | None:
        content = row.get("content")
        if not content.strip():
            return None
        published_at = datetime.fromtimestamp(int(row.get("published_at")))
        return EvidenceDocument(
            platform=row["platform"],
            source_table=row["source_table"],
            mysql_primary_key=row["mysql_primary_key"],
            content=content,
            published_at=published_at,
            engagement={field.name: float(row[f"eng_{field.name}"]) for field in fields(Engagement)},
            hotness_score=row["hotness_score"],
        )