"""Host 与 Report 共享的电商章节结构化研判契约。"""

from pydantic import BaseModel, Field


class SectionJudgement(BaseModel):
    """Host 对单个章节的结构化研判。"""

    section_key: str
    aligned_points: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    risk_signals: list[str] = Field(default_factory=list)
    opportunity_signals: list[str] = Field(default_factory=list)
    affected_objects: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    evidence_review: str
    host_judgement: str

    @property
    def content(self) -> str:
        return render_judgement_markdown(self)


def format_markdown_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) or "暂无"


def render_judgement_markdown(judgement: SectionJudgement) -> str:
    heading_level = "#" * 3
    blocks = [
        judgement.host_judgement or "暂无研判",
        f"{heading_level} 双方一致观点\n",
        format_markdown_list(judgement.aligned_points),
        f"{heading_level} 关键分歧\n",
        format_markdown_list(judgement.conflicts),
        f"{heading_level} 风险信号\n",
        format_markdown_list(judgement.risk_signals),
        f"{heading_level} 机会信号\n",
        format_markdown_list(judgement.opportunity_signals),
        f"{heading_level} 受影响对象\n",
        format_markdown_list(judgement.affected_objects),
        f"{heading_level} 建议动作\n",
        format_markdown_list(judgement.recommended_actions),
        f"{heading_level} 证据情况与信息缺口\n",
        judgement.evidence_review or "暂无补充",
    ]
    return "\n\n".join(blocks)
