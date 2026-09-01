from fastapi import APIRouter

from app.dependencies import ResearchServiceDep
from app.schemas.research_schema import (
    ResearchExample,
    ResearchExamplesResponse,
    ResearchRequest,
    ResearchResponse,
    ResearchResultsResponse,
)

research_router = APIRouter(
    prefix='/api/research',
    tags=['研究路由'],
)


@research_router.get(
    "/examples",
    response_model=ResearchExamplesResponse,
    description="获取电商业务 Demo 研究题目",
)
def get_research_examples_endpoint(service: ResearchServiceDep):
    return ResearchExamplesResponse(
        examples=[ResearchExample.model_validate(item) for item in service.get_research_examples()]
    )


@research_router.post("", response_model=ResearchResponse, description='开始研究接口')
async def start_research_endpoint(payload: ResearchRequest, service: ResearchServiceDep):
    return ResearchResponse(task_id=service.research(payload.query))


@research_router.get("/results", response_model=ResearchResultsResponse, description='获取研究结果接口')
def get_research_result_endpoint(task_id: str, service: ResearchServiceDep):
    resolved_task_id, research_results = (service.get_research_results(task_id))
    return ResearchResultsResponse(task_id=resolved_task_id,results=research_results)
