from fastapi import APIRouter

from app.dependencies import ResearchServiceDep
from app.schemas.research_schema import ResearchResponse, ResearchRequest, ResearchResultsResponse

research_router = APIRouter(
    prefix='/api/research',
    tags=['研究路由'],
)


@research_router.post("", response_model=ResearchResponse, description='开始研究接口')
async def start_research_endpoint(payload: ResearchRequest, service: ResearchServiceDep):
    return ResearchResponse(task_id=service.research(payload.query))


@research_router.get("/results", response_model=ResearchResultsResponse, description='获取研究结果接口')
def get_research_result_endpoint(task_id: str, service: ResearchServiceDep):
    resolved_task_id, research_results = (service.get_research_results(task_id))
    return ResearchResultsResponse(task_id=resolved_task_id,results=research_results)
