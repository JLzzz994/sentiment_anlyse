"""MySQL 异步引擎与会话工厂的生命周期管理"""
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from engines.contracts.settings import get_settings


class DatabaseConnectionManager:
    """封装MySQL 异步引擎与会话工厂与释放"""

    def __init__(self):
        # 配置 引擎 与会话工厂
        self._settings = get_settings()
        self._async_engine: AsyncEngine | None = None
        self._async_session_factory: async_sessionmaker[AsyncSession] | None = None

    def get_async_engine(self) -> AsyncEngine:
       """返回MySQL 异步引擎"""
       if self._async_engine is None:
           self._async_engine = create_async_engine(
               url=self._build_db_url(),
               echo=False, #不把数据打印打控制台
           )
       return self._async_engine

    def get_async_session_factory(self)->async_sessionmaker[AsyncSession]:
        """返回异步引擎会话工厂"""
        if self._async_session_factory is None:
            self._async_session_factory = async_sessionmaker(
                bind=self.get_async_engine(),
                expire_on_commit=False
            )
        return self._async_session_factory

    async def dispose_engine(self)->None:
        """释放MySQL 异步引擎"""
        self._async_session_factory = None
        if self._async_engine is not None:
            try:
                await self._async_engine.dispose()
            finally:
                self._async_engine = None

    def _build_db_url(self):
        """依据配置项拼接MySQL 异步连接url"""
        return URL.create(
            drivername="mysql+aiomysql",
            username=self._settings.DB_USER,
            password=self._settings.DB_PASSWORD,
            host=self._settings.DB_HOST,
            port=self._settings.DB_PORT,
            database=self._settings.DB_NAME,
        )


database_connection_manager = DatabaseConnectionManager()