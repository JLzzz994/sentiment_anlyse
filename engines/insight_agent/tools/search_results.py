from dataclasses import dataclass, field

from engines.contracts.evidence import EvidenceDocument


@dataclass(slots=True)
class SearchResult:
    """MySQL 召回结果集合"""
    retrieval_channel: str
    retrieval_results: list[EvidenceDocument] = field(default_factory=list)


@dataclass(slots=True)
class SearchHit:
    """Milvus 包含检索元数据的单条向量命中结果"""
    retrieval_score: float
    retrieval_channel: str
    retrieval_document: EvidenceDocument
