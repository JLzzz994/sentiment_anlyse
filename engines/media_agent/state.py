from engines.contracts.evidence import EvidenceRecord
from engines.contracts.research_graph_state import SectionState, ResearchGraphState
from engines.media_agent.web_search.search_results import SearchTool


class MediaSectionState(SectionState):
    """公域搜索工具和搜索关键词 的章节状态"""
    search_tool: SearchTool
    search_keywords: list[str]


class MediaState(ResearchGraphState[MediaSectionState], total=False):
    """
    媒体智能体 LangGraph 全局状态定义
    task_id:str
    query:str
    role:RoleKey
    sections:list[SectionStateT]{
    section_key: str
    title: str
    body: NotRequired[str] # 暂时不需要定义 章节摘要
    search_tool : SearchTool
    search_keywords:list[str]
    }
    cursor:int
    final_report:str
    """
    section_evidence_records: list[list[EvidenceRecord]] # 全部章节的证据列表
    section_queries: list[str] # 章节关键词列表
