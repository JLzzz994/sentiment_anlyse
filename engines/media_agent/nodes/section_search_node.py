import asyncio
from itertools import zip_longest
from typing import Any

from loguru import logger

from engines.common.research_graph_runtime import ResearchNode, ResearchRunContext
from engines.contracts.agent_roles import ROLE_INFOS
from engines.contracts.evidence import EvidenceRecord
from engines.media_agent.state import MediaState, MediaSectionState
from engines.media_agent.web_search.retrieval_service import MediaRetrievalService


class SectionSearchNode(ResearchNode):
    """遍历章节组合关键词检索并 聚合去重证据"""

    def __init__(self, ctx: ResearchRunContext):
        super().__init__(ctx)
        self._retrieval_service = MediaRetrievalService()

    async def __call__(self, state: MediaState) -> dict[str, Any]:
        """遍历章节执行检索并去重 产出证据池"""
        role = state['role']
        role_info = ROLE_INFOS[role]
        logger.info(f"{role_info.agent_name} 开始执行公域信息搜索")

        query: str = state["query"]
        sections: list[MediaSectionState] = state.get('sections', [])
        section_evidence_records = []
        section_queries = []

        for section in sections:
            tool = section.get("search_tool")
            keywords = section.get("search_keywords")
            queries = [f"{query} {keyword}".strip() for keyword in keywords]
            query_results = await asyncio.gather(
                *(self._retrieval_service.retrieval_evidence(tool, query) for query in queries),
            )
            section_records = _merge_query_results(query_results)
            section_evidence_records.append(section_records)
            section_queries.append(
                "\n".join(f"[{tool}] {query}" for query in queries)
            )

        logger.info(f"{role_info.agent_name} 完成执行公域信息搜索")
        return {"section_evidence_records": section_evidence_records,
                "section_queries": section_queries}


def _merge_query_results(query_results: list[list[EvidenceRecord]]) -> list[EvidenceRecord]:
    """各查询内按相关分降序排列,再轮询合并并按证据id去重"""
    selected:list[EvidenceRecord]=[]
    seen_ids:set[str]=set()
    ranked_results = [ sorted(
        records,
        key=lambda record:record.retrieval_meta.channel_scores.get("web_call"),
        reverse=True
    ) for records in query_results]
    for ranked_records in zip_longest(*ranked_results):
        for record in ranked_records:
            if record is None or record.id in seen_ids:
                continue
            seen_ids.add(record.id)
            selected.append(record)
    return selected
        
