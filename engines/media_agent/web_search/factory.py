from engines.media_agent.web_search.base import BaseSearchClient
from engines.media_agent.web_search.providers import AnspireSearchClient
from engines.media_agent.web_search.search_results import SearchProviderResponse


class WebSearchClient:
    """基于Anspire Provider 的Web 检索统一入口"""

    def __init__(self):
        """实例化当前唯一的Anspire Provider客户端"""
        self._client: BaseSearchClient = AnspireSearchClient()

    async def comprehensive_search(self, query: str) -> SearchProviderResponse:
        """委托具体Provider 执行综合检索"""
        return await self._client.comprehensive_search(query)

    async def source_search(self, query: str) -> SearchProviderResponse:
        """委托具体 Provider 执行溯源检索"""
        return await self._client.source_search(query)

    async def realtime_search(self, query: str) -> SearchProviderResponse:
        """委托具体 Provider 执行实时检索"""
        return await self._client.realtime_search(query)
