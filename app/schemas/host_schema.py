from pydantic import BaseModel, Field


class HostDiscussionRecord(BaseModel):
    """主持人讨论区单条发言记录"""
    task_id:str
    source:str
    message_text:str
    sent_at:str
    dimension_key:str

class HostDiscussionRecordsResponse(BaseModel):
    """主持人讨论区发言记录列表响应"""
    discussion_records:list[HostDiscussionRecord]=Field(default_factory=list)

class HostJudgementItem(BaseModel):
    section_key: str
    title: str
    aligned_points: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    risk_signals: list[str] = Field(default_factory=list)
    opportunity_signals: list[str] = Field(default_factory=list)
    affected_objects: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    evidence_review: str = ""
    host_judgement: str = ""


class HostJudgementsResponse(BaseModel):
    task_id: str
    sections: list[HostJudgementItem] = Field(default_factory=list)
