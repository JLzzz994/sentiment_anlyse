from fastapi import APIRouter,Request
from sse_starlette import EventSourceResponse

from app.dependencies import get_research_progress_stream

sse_router = APIRouter(tags=['SSE实时事件流路由'])

# GET /api/events/stream?task_id=任务ID
@sse_router.get('/api/events/stream')
async def stream_research_progress(request:Request,task_id:str):
    return EventSourceResponse(
        get_research_progress_stream().stream_research_progress(request,task_id)
    )
