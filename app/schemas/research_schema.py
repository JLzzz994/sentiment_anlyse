"""
REST层需要的schema 它只定义 http 输入输出,不放业务逻辑
"""

from pydantic import BaseModel, Field, field_validator


class ResearchRequest(BaseModel):
    """启动研究任务的请求体"""

    query: str = Field(..., description="研究主题")

    @field_validator("query")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("研究主题不能为空")
        return value


class ResearchResponse(BaseModel):
    """启动研究任务后的响应"""
    task_id: str


class ResearchResultsResponse(BaseModel):
    """指定任务已完成的角色报告"""
    task_id: str
    results: dict[str, str] = Field(default_factory=dict)
