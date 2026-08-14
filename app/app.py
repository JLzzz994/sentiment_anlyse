from fastapi import FastAPI

from app.dependencies import get_lifecycle_manager
from app.exceptions.exception_handlers import register_exception_handlers
from app.routers.rest.host_router import host_router
from app.routers.rest.report_router import report_router
from app.routers.rest.research_router import research_router
from app.routers.rest.system_router import system_router
from app.routers.sse.research_progress import sse_router


async def lifespan(app:FastAPI):
    """应用启停时注册与关闭生命周期管理器"""
    lifecycle_manager = get_lifecycle_manager()
    try:
        lifecycle_manager.register()
        yield
    finally:
        await lifecycle_manager.shutdown()


app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.include_router(research_router)
app.include_router(host_router)
app.include_router(report_router)
app.include_router(system_router)
app.include_router(sse_router)