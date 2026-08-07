"""Milvus 知识库同步器: 从MySQL 全亮拉取并写入Milvus 集合"""
import asyncio

from loguru import logger

from engines.insight_agent.tools.db_connection import database_connection_manager
from engines.insight_agent.tools.vector.repository import VectorSearchRepository
from engines.insight_agent.tools.vector.sync.reader import DocumentRecordReader


class DocumentRecordSynchronizer:
    """知识库同步器"""

    def __init__(self):
        self._vector_repository = VectorSearchRepository()
        self._source_reader = DocumentRecordReader()

    async def full_sync(self, drop_exists: bool = False) -> int:
        """全量同步MySQL 文档到 Milvus, 返回入库文档数"""
        all_documents = await self._source_reader.read_all_documents()
        await asyncio.to_thread(
            self._vector_repository.ensure_collection,
            drop_exists=drop_exists
        )
        count = await asyncio.to_thread(
            self._vector_repository.upsert_documents,all_documents,
        )
        return count

async def main():
    logger.info("开始启动 Milvus 知识库全量同步测试...")
    synchronizer = DocumentRecordSynchronizer()
    # 看起来是删表 实质是清空数据trunk
    try:
        count = await synchronizer.full_sync(drop_exists=True)
        logger.success(f"知识库全量同步测试完成,共插入{count}条记录.")
    finally:
        await database_connection_manager.dispose_engine()

if __name__ == '__main__':
    asyncio.run(main())