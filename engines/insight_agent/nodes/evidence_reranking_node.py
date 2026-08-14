from typing import Any

from loguru import logger

from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.agent_roles import ROLE_INFOS, role_display_name
from engines.contracts.evidence import EvidenceRecord, RetrievalMeta

"""
class ResearchNode(ABC):

    def __init__(self, ctx: ResearchRunContext):
        self.ctx = ctx

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:

"""


class EvidenceRerankingNode(ResearchNode):
    """合并重复召回证据并计算统一重排分"""

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """合并重复召回指标、计算排名分数并构建证据索引"""
        agent_name = role_display_name(state["role"])
        logger.info(f"{agent_name} 开始召回证据的去重和重排序")
        # 1. 合并去重
        merged_records: list[EvidenceRecord] = _dedupe_and_merge(state.get("retrieved_records"))
        # 2. 重新计算得分 证据id,score
        # (vector_call *0.5 + db_call * 0.5 ) *0.6 + (hotness_score/max_hot_score) * 0.4
        rerank_records: dict[str, float] = _calculate_rerank_scores(merged_records)
        # 3. 重新排序
        ordered_records: list[EvidenceRecord] = sorted(merged_records,
                                                       key=lambda record: rerank_records.get(record.id, float('-inf')),
                                                       reverse=True, )

        logger.info(f"{agent_name} 完成召回证据的去重和重排序")
        return {"records_by_id": {record.id: record for record in ordered_records},
                "rerank_scores": rerank_records}


def _dedupe_and_merge(retrieved_records: list[EvidenceRecord]) -> list[EvidenceRecord]:
    records_by_id: dict[str, EvidenceRecord] = {}
    for record in retrieved_records:
        existing_record = records_by_id.get(record.id)
        if existing_record is None:
            records_by_id[record.id] = record
            continue
        existing_retrieval_meta = existing_record.retrieval_meta
        records_by_id[record.id] = EvidenceRecord(
            evidence_document=existing_record.evidence_document,
            retrieval_meta=RetrievalMeta(
                matched_queries=list(
                    set(existing_retrieval_meta.matched_queries + record.retrieval_meta.matched_queries)),
                channel_scores={**existing_retrieval_meta.channel_scores, **record.retrieval_meta.channel_scores}
            )
        )
    return list(records_by_id.values())


def _retrieval_score(record:EvidenceRecord)->float:
    """按渠道权重加权召回得分 并截断至1"""
    channel_scores:dict[str,float] = record.retrieval_meta.channel_scores
    score = (channel_scores.get("vector_call",0.0) * 0.5 + channel_scores.get("db_call",0.0) * 0.5 )
    return score


def _calculate_rerank_scores(merged_records: list[EvidenceRecord]) -> dict[str, float]:
    max_hot_score = max(record.evidence_document.hotness_score for record in merged_records)
    return {record.id: _retrieval_score(record) * 0.6 + (record.evidence_document.hotness_score / max_hot_score) * 0.4
            for record in merged_records}
