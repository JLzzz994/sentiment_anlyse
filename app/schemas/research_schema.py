"""REST 层研究任务输入输出 schema。"""

from pydantic import BaseModel, Field, field_validator


class ResearchRequest(BaseModel):
    """启动电商规则/口碑研判任务。"""

    query: str = Field(
        ...,
        description=(
            "研究主题，例如：淘宝售后规则调整对服饰类商家的履约与退款风险影响；"
            "或某商品近30天差评是否形成集中问题。"
        ),
    )

    @field_validator("query")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("研究主题不能为空")
        return value


class ResearchResponse(BaseModel):
    task_id: str


class ResearchResultsResponse(BaseModel):
    task_id: str
    results: dict[str, str] = Field(default_factory=dict)
