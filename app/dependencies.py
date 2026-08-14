"""
现在把 Service 接到 FastAPI。，
它统一管理单例，
避免每次请求都重新创建 OrchestratorAgent、ReportEngine 和 SSE 订阅池。
"""

from typing import Annotated

from fastapi import Depends

from app.services.host.host_service import HostService
from app.services.lifecycle.lifecycle_service import AppLifecycleManager
from app.services.report.report_service import ReportService
from app.services.research.research_service import ResearchService
from app.services.sse.research_progress_stream import ResearchProgressStream
from app.services.system.system_service import SystemConfigService

_research_service = ResearchService()
_report_service = ReportService()
_host_service = HostService()
_config_service = SystemConfigService()
_research_progress_stream = ResearchProgressStream()
_lifecycle_manager = AppLifecycleManager(_host_service, _research_progress_stream)


def get_research_service() -> ResearchService:
    return _research_service


def get_report_service() -> ReportService:
    return _report_service


def get_host_service() -> HostService:
    return _host_service


def get_config_service() -> SystemConfigService:
    return _config_service

def get_research_progress_stream()->ResearchProgressStream:
    return _research_progress_stream

def get_lifecycle_manager() -> AppLifecycleManager:
    """提供全局生命周期管理器单例"""
    return _lifecycle_manager

ResearchServiceDep = Annotated[ResearchService,Depends(get_research_service)]
ReportServiceDep = Annotated[ReportService,Depends(get_report_service)]
HostServiceDep = Annotated[HostService, Depends(get_host_service)]
SystemConfigServiceDep = Annotated[SystemConfigService, Depends(get_config_service)]

