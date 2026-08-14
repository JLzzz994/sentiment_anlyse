from typing import TypedDict, Any

from engines.common.events import HostDiscussionMessageEvent
from engines.contracts.judgement import SectionJudgement
from engines.host_agent.section_pair_store import SectionPairStore


class HostState(TypedDict,total=False):
    """Host LangGraph 的事件输入、章节配对 与 研判状态"""
    task_id:str # 任务id
    event_payload:dict[str,Any] # 章节摘要 五个章节对应的章节准备事件类型的数据包
    section_pair_store:SectionPairStore # 章节对存储 存和取 SectionPair
    judgements:list[SectionJudgement] # 5个章节的研判结果
    discussion_events:list[HostDiscussionMessageEvent] # 当次循环的讨论事件 三个角色讨论区要展示的数据对象
    section_judgement:SectionJudgement # 当前的章节研判