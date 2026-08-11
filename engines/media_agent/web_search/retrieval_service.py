"""Media Web 检索编排与证据标准化"""
import asyncio
import hashlib

from httpx._urlparse import urlparse

from engines.contracts.evidence import EvidenceRecord, EvidenceDocument, RetrievalMeta
from engines.media_agent.web_search.factory import WebSearchClient
from engines.media_agent.web_search.search_results import SearchTool, SearchProviderResponse


class MediaRetrievalService:
    """执行单词Web检索并将Provider结果归一化为证据"""

    def __init__(self):
        self._web_search_client = WebSearchClient()

    async def retrieval_evidence(self, tool_name: SearchTool, query: str) -> list[EvidenceRecord]:
        """按工具执行web 检索并返回标准化证据,失败时异常上抛"""
        response = await  self._search_webpage(tool_name, query)
        return _map_to_evidence_record(response, query)

    async def _search_webpage(self, tool_name: SearchTool, query: str) -> SearchProviderResponse:
        """按工具类型分派综合、溯源或实时检索"""
        match tool_name:
            case "source_search":
                return await self._web_search_client.source_search(query)
            case "realtime_search":
                return await self._web_search_client.realtime_search(query)
            case _:
                return await self._web_search_client.comprehensive_search(query)


def _extract_source_name(url: str) -> str:
    """从网页url中 提取标准化来源的域名"""
    hostname = urlparse(url).host.lower()
    return hostname.removeprefix("www.")


def _generate_content_hash_id(content: str) -> str:
    """对标准化内容生成证据标识, 内容为空时回退url"""
    normalized_content = " ".join(content.split())
    raw_key = normalized_content.strip()
    return hashlib.md5(raw_key.encode("utf-8")).hexdigest()


def _map_to_evidence_record(response: SearchProviderResponse, query: str) -> list[EvidenceRecord]:
    """将网页结果映射为带稳定哈希id的证据记录"""
    records: list[EvidenceRecord] = []
    for page in response.webpages:
        source_name = _extract_source_name(page.url)
        content = page.content
        records.append(EvidenceRecord(
            evidence_document=EvidenceDocument(
                platform=source_name,
                source_table="webpage",
                source_id=_generate_content_hash_id(content),
                content=content,
                published_at=page.date,
                url=page.url,
                title=page.title,
                source_name=source_name,
            ),
            retrieval_meta=RetrievalMeta(
                matched_queries=[query],
                channel_scores={"web_call": page.score}
            )
        ))
    return records


async def main():
    service = MediaRetrievalService()

    query = "白海豚影响"
    tools: list[SearchTool] = ["comprehensive_search", "source_search", "realtime_search"]
    for tool in tools:
        print(f"测试工具: {tool} \n")
        records = await service.retrieval_evidence(tool_name=tool, query=query)

        print(f"共获取 {len(records)}条证据: \n")
        for i, rec in enumerate(records, start=1):
            doc = rec.evidence_document
            score = rec.retrieval_meta.channel_scores.get("web_call")

            print(f"[{i}] 站点: {doc.platform}")
            print(f"    来源: {doc.source_name}")
            print(f"    记录唯一ID: {doc.source_id}")
            print(f"    标题: {doc.title}")
            print(f"    url: {doc.url}")
            print(f"    时间: {doc.published_at}")
            print(f"    得分: {score}")
            print(f"    摘要: {doc.content}...\n")


if __name__ == "__main__":
    asyncio.run(main())
