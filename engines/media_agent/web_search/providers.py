import asyncio
import datetime
from typing import Any

from engines.common.retries import with_retry
from engines.contracts.settings import get_settings
from engines.media_agent.web_search.base import BaseSearchClient
from engines.media_agent.web_search.search_results import SearchProviderResponse, WebpageResult

# source_search 只限定电商平台官方域名；是否为规则原文仍由 Media Agent 基于标题/内容判断。
OFFICIAL_ECOMMERCE_SOURCES = (
    "taobao.com,tmall.com,jd.com,pinduoduo.com,"
    "jinritemai.com,kwaixiaodian.com"
)
PUBLIC_DISCUSSION_SOURCES = (
    "weibo.com,zhihu.com,toutiao.com,bilibili.com,xiaohongshu.com"
)


class AnspireSearchClient(BaseSearchClient):
    """Anspire Web 检索 Provider 实现。"""

    def __init__(self):
        super().__init__()
        self.api_key = get_settings().ANSPIRE_API_KEY
        self.base_url = get_settings().ANSPIRE_BASE_URL
        self.headers = self.build_request_headers(self.api_key)

    async def comprehensive_search(self, query: str) -> SearchProviderResponse:
        return await self._execute_search(query=query, top_k=15)

    async def source_search(self, query: str) -> SearchProviderResponse:
        """在主流电商平台官方域名执行规则/公告溯源检索。"""
        return await self._execute_search(
            query=query,
            top_k=10,
            insite=OFFICIAL_ECOMMERCE_SOURCES,
        )

    async def realtime_search(self, query: str) -> SearchProviderResponse:
        """在近一周公开社区范围内检索商家反馈与商品口碑。"""
        to_time = datetime.datetime.now()
        from_time = to_time - datetime.timedelta(weeks=1)
        return await self._execute_search(
            query=query,
            top_k=5,
            insite=PUBLIC_DISCUSSION_SOURCES,
            from_time=from_time.strftime("%Y-%m-%d %H:%M:%S"),
            to_time=to_time.strftime("%Y-%m-%d %H:%M:%S"),
        )

    @with_retry
    async def _execute_search(
        self,
        query: str,
        top_k: int,
        insite: str = "",
        from_time: str = "",
        to_time: str = "",
    ) -> SearchProviderResponse:
        params = {
            "query": query,
            "top_k": top_k,
            "Insite": insite,
            "FromTime": from_time,
            "ToTime": to_time,
        }
        response = await self.send_request(
            method="GET",
            url=self.base_url,
            kwargs={"headers": self.headers, "params": params},
        )
        return self._process_response(response, query)

    @staticmethod
    def _process_response(
        response_dict: dict[str, Any], query: str
    ) -> SearchProviderResponse:
        results: list[dict] = response_dict.get("results", [])
        webpages = [
            WebpageResult(
                title=result.get("title"),
                url=result.get("url"),
                content=result.get("content"),
                date=result.get("date"),
                score=result.get("score"),
            )
            for result in results
        ]
        return SearchProviderResponse(query=query, webpages=webpages)


async def main():
    client = AnspireSearchClient()
    query = "淘宝 售后 规则 退款"

    for tool_name, call in (
        ("comprehensive_search", client.comprehensive_search),
        ("source_search", client.source_search),
        ("realtime_search", client.realtime_search),
    ):
        result = await call(query)
        print(f"[{tool_name}] {result.query}: {len(result.webpages)}")


if __name__ == "__main__":
    asyncio.run(main())
