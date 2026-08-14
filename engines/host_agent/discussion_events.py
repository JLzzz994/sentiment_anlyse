
from engines.common.events import HostDiscussionMessageEvent
from engines.contracts.judgement import SectionJudgement
from engines.host_agent.models import AgentSectionOutput


def build_agent_discussion_event(task_id: str, output: AgentSectionOutput) -> HostDiscussionMessageEvent:
    """构造Insight 或 Media 的章节讨论事件"""
    return HostDiscussionMessageEvent(
        task_id=task_id,
        source=output.source,
        section_key=output.section_key,
        content=output.body[:2000]
    )

def build_judgement_discussion_event(task_id:str,judgement:SectionJudgement,)->HostDiscussionMessageEvent:
    """构造Host单章节研判讨论事件"""
    return HostDiscussionMessageEvent(
        task_id=task_id,
        source="host",
        section_key=judgement.section_key,
        content=judgement.content # 把研判总结渲染了
    )