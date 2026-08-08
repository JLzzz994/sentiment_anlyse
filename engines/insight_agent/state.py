from engines.contracts.evidence import EvidenceRecord
from engines.contracts.research_graph_state import ResearchGraphState, SectionState

"""
class SectionState(TypedDict):
    完成规划后在研究图中持续传递的章节状态
    section_key: str
    title: str
    body: NotRequired[str] # 暂时不需要定义 章节摘要

SectionStateT = TypeVar("SectionStateT",bound=SectionState)

class ResearchGraphState(TypedDict,Generic[SectionStateT],total=False):
    研究图全流程共享的运行标识 章节 与 报告状态
    task_id:str
    query:str
    role:RoleKey
    sections:list[SectionStateT]
    cursor:int
    final_report:str
"""


class InsightState(ResearchGraphState[SectionState], total=False):
    """LangGraph 全局状态: 证据处理结果、章节列表与游标"""
    retrieved_records: list[EvidenceRecord] # 证据对象列表
    records_by_id: dict[str, EvidenceRecord] # 证据id : 证据对象 的映射关系
    rerank_scores: dict[str, float] # 证据id : 证据分数
    section_record_ids: dict[str, list[str]] # 章节key: 证据id列表
    section_evidence_records: list[list[EvidenceRecord]] # 外层5个章节 内层每个章节对应的证据id列表
