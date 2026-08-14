from app.services.host.host_service import HostService
from app.services.sse.research_progress_stream import ResearchProgressStream
from engines.common.task_manager import research_task_manager


class AppLifecycleManager:
    """应用生命周期管理器: 统一启动与关闭后台服务组件及引擎共享资源"""

    def __init__(
            self,
            host_service: HostService,
            research_progress_stream: ResearchProgressStream
    ):
        """初始化生命周期管理器并注入依赖组件"""
        self.host_service = host_service
        self.research_progress_stream = research_progress_stream

    def register(self):
        """统一注册并启动所有关联的后台服务组件"""
        # 1. 先订阅进度事件,避免任务启动后丢掉第一条进度
        self.research_progress_stream.register_progress_update()

        # 2. 讨论缓冲用于保存Host Agent 的章节讨论消息
        self.host_service.register_discussion_buffer()
        # 3. Host listener 监听 SECTION_READY 驱动章节研判
        self.host_service.register_host_listener()

    async def shutdown(self):
        """统一注销并停止所有关联的后台服务组件,释放持有的资源"""
        self.research_progress_stream.stop_progress_update()
        # 1. 停止讨论缓冲服务 释放监听
        self.host_service.stop_discussion_buffer()
        # 2. 停止Host 章节监听worker
        self.host_service.stop_host_listener()
        # 3. 取消仍在执行的研究/报告后台任务
        await research_task_manager.cancel_all_tasks()
