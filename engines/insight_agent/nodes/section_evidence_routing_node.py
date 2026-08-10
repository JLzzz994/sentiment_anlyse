from collections import defaultdict
from functools import lru_cache
from typing import Any

import numpy as np
from loguru import logger

from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.agent_roles import ROLE_INFOS
from engines.contracts.evidence import EvidenceRecord
from engines.contracts.section_definitions import get_insight_routing_rules, SECTION_DEFINITIONS
from engines.contracts.settings import get_settings


class SectionEvidenceRoutingNode(ResearchNode):
    """将重排证据按规则或语义相似度路由到固定章节"""

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        return section_record_ids: dict[str, list[str]] # 章节key: 证据id列表
        """
        role = state['role']
        role_info = ROLE_INFOS[role]
        logger.info(f"{role_info.agent_name} 开始章节分配证据")
        # records_by_id: dict[str, EvidenceRecord] # 证据id : 证据对象 的映射关系
        records: list[EvidenceRecord] = list(state.get("records_by_id").values())
        # 1. 语义分配
        if _is_semantic_enabled(records):
            section_record_ids = _route_by_semantics(records)
        else:
            section_record_ids = _route_by_rules(records)

        logger.info(f"{role_info.agent_name} 完成章节分配证据")
        return {"section_record_ids": section_record_ids}


def _is_semantic_enabled(records: list[EvidenceRecord]) -> bool:
    settings = get_settings()
    return (
            bool(records) and
            settings.INSIGHT_SEMANTIC_ROUTING_ENABLED and
            bool(settings.INSIGHT_SEMANTIC_ROUTING_MODEL)
    )


def _route_by_semantics(records: list[EvidenceRecord]):
    """逐条计算与固定章节 关键词向量的相似度,并路由到最相关章节"""
    # 1. 提取并拼接证据文本内容
    contents = [(
        f"{' '.join(record.retrieval_meta.matched_queries)} "
        f"{record.evidence_document}"
    ) for record in records]
    # 2. 批量编码生成证据归一化向量
    record_vectors = _get_embedding_model().encode(
        contents,
        normalize_embeddings=True
    )
    # 3. 读取缓存的固定章节以及向量
    section_keys, section_vectors = _get_section_vectors()
    # 4. 计算相似度矩阵 30 * 5
    similarities = np.dot(record_vectors, section_vectors.T)
    # 5. 取每条证据对应的最相关章节索引
    best_indices = np.argmax(similarities, axis=-1)
    # 6. 组装结果
    section_record_ids: dict[str, list[str]] = defaultdict(list)
    for best_idx, record in zip(best_indices, records):
        section_key = section_keys[best_idx]
        section_record_ids[section_key].append(record.id)
    return section_record_ids


@lru_cache
def _get_embedding_model():
    """惰性加载 章节语义路由 使用的嵌入模型"""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(str(get_settings().INSIGHT_SEMANTIC_ROUTING_MODEL))


def _get_section_vectors():
    """缓存固定章节 !关键词! 的归一化向量"""
    rules = get_insight_routing_rules()
    section_texts: list[str] = [f"{SECTION_DEFINITIONS[section_key].title}: {' '.join(keywords)}" for
                                section_key, keywords in
                                rules.items()]
    section_vectors = _get_embedding_model().encode(section_texts, normalize_embeddings=True)
    section_keys = list(rules.keys())
    return section_keys, section_vectors


def _route_by_rules(records:list[EvidenceRecord])->dict[str,list[str]]:
    """按关键词 规则 将证据路由到首个匹配章节"""
    section_record_ids: dict[str, list[str]] = defaultdict(list)
    # section_key : list[keyword] 全部5个章节
    rules = get_insight_routing_rules()
    for record in records:
        # query 关键词  + 内容
        text = (
            f"{' '.join(record.retrieval_meta.matched_queries)} "
            f"{record.evidence_document.content}"
        )
        # 用 章节关键词 在 text{query关键词+内容} 中进行匹配
        # 找到就得到  当前这条 record 对应的 section_key ; 否则None
        section_key = next(
            (section_key for section_key,keywords in rules.items() if any(keyword in text for keyword in keywords)),
            None,
        )
        if section_key is not None:
            section_record_ids[section_key].append(record.id)
    return section_record_ids