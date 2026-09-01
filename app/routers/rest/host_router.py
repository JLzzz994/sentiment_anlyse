from fastapi import APIRouter

from app.dependencies import HostServiceDep
from app.schemas.host_schema import HostDiscussionRecordsResponse, HostJudgementsResponse

host_router = APIRouter(prefix='/api/host',tags=['主持人 Agent'])

@host_router.get("/discussion",response_model=HostDiscussionRecordsResponse,description="获取讨论区里收集到的发言记录")
def get_host_discussion_records_endpoint(
        service:HostServiceDep,
        task_id:str
):
    """返回讨论区发言记录"""
    discussion_records = service.get_discussion_records(task_id)
    return HostDiscussionRecordsResponse(**discussion_records)

@host_router.get(
    "/judgements",
    response_model=HostJudgementsResponse,
    description="获取 Host 五章结构化研判",
)
def get_host_judgements_endpoint(service: HostServiceDep, task_id: str):
    return HostJudgementsResponse.model_validate(service.get_judgements(task_id))
