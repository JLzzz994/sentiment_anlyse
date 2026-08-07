from fastapi import FastAPI

from app.exceptions.exception_handlers import register_exception_handlers
from app.routers.system_router import system_router

app = FastAPI()

register_exception_handlers(app)

app.include_router(system_router)