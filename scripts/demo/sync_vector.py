"""将 Demo 私域统一视图全量同步到 Milvus。"""

import asyncio
from loguru import logger

from engines.insight_agent.tools.db_connection import database_connection_manager
from engines.insight_agent.tools.vector.sync.synchronizer import DocumentRecordSynchronizer


async def main() -> None:
    synchronizer = DocumentRecordSynchronizer()
    try:
        count = await synchronizer.full_sync(drop_exists=True)
        logger.success(f"Demo 私域证据同步完成，共写入 Milvus {count} 条")
    finally:
        await database_connection_manager.dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())
