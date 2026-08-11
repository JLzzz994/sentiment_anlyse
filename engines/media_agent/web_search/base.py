from abc import ABC, abstractmethod
from typing import TypedDict, Any

import httpx

from engines.media_agent.web_search.search_results import SearchProviderResponse


class HttpRequestOptions(TypedDict, total=False):
    """统一http 请求的参数选项类型"""
    headers: dict[str, str]
    params: dict[str, Any]
    json: dict[str, Any]


class BaseSearchClient(ABC):
    """Web搜索Provider 的抽象能力  基类"""

    def __init__(self):
        """基类空构造,子类完成具体初始化"""
        pass

    @staticmethod
    def build_request_headers(api_key: str, *, accept: str = "application/json") -> dict[str, str]:
        """构造 Bearer JSON 请求头"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": accept,
        }
        return headers

    async def send_request(
            self,
            method: str,
            url: str,
            kwargs: HttpRequestOptions,
    ) -> dict[str, Any]:
        """用httpx 异步发起请求并返回JSON"""
        async with httpx.AsyncClient(timeout=60, trust_env=False) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=kwargs.get("headers"),
                params=kwargs.get("params"),
                json=kwargs.get("json"),
            )
            response.raise_for_status()
            data = response.json()
        return data

    @abstractmethod
    async def comprehensive_search(self, query: str) -> SearchProviderResponse:
        """
        综合检索某主题的全面公开媒体信息
        """
    @abstractmethod
    async def source_search(self, query: str) -> SearchProviderResponse:
        """
        溯源检索 可以核查的原始网页出处
        return SearchProviderResponse {query webpages}
        """
    @abstractmethod
    async def realtime_search(self,query:str)->SearchProviderResponse:
        """实时检索最新报道与传播动态"""