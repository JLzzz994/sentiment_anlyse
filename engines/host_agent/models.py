from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AgentSectionOutput:
    """单个研究 Agent发布的章节输出"""
    source: str
    section_key: str
    body: str

    @classmethod
    def from_section_ready_event(cls, event_payload: dict[str, Any]) -> "AgentSectionOutput":
        """从章节就绪事件载荷构造Agent章节输出"""
        return cls(
            source=event_payload['source'],
            section_key=event_payload['section_key'],
            body=event_payload['body'],
        )


@dataclass(slots=True)
class AgentSectionPair:
    """同一章节的Insight 与Media输出配对"""
    section_key: str
    title: str
    insight: AgentSectionOutput
    media: AgentSectionOutput
