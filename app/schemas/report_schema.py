from pydantic import BaseModel, Field


class GenerateReportRequest(BaseModel):
    """触发最终报告生成的请求体"""

    task_id: str = Field(
        ...,
        min_length=1,
        description="关联的研究任务id"
    )


class ReportStatusResponse(BaseModel):
    """最终报告输入文件的准备状态"""
    task_id: str
    prepared: bool = False
    found_files: list[str] = Field(default_factory=list)


class GenerateReportResponse(BaseModel):
    """报告生成任务已创建后的响应"""
    generation_id: str
    task_id: str


