from typing import Callable, Awaitable

from loguru import logger

from engines.common.events import publish_role_error, RoleErrorEvent, publish_role_result, RoleResultEvent, \
    publish_role_progress, RoleProgressEvent
from engines.common.llm import LLMClient
from engines.common.loggers import route_log_by_role
from engines.common.reports import get_output_dir
from engines.common.research_graph_runtime import ProgressCallback, ProgressUpdate
from engines.common.task_manager import research_task_manager
from engines.contracts.agent_roles import RoleKey
from engines.insight_agent.agent import insight_agent_handler
from engines.media_agent.agent import media_agent_handler

# 第一个参数是方法的参数, 第二个参数是方法的返回值

"""
表示注册函数得有
async def 某个_agent(
    run_id: str,
    query: str,
    role: ResearchRoleKey,
    llm_client: LLMClient,
    output_dir: str,
    progress_callback: ProgressCallback,
) -> None:
    ...
"""
AGENT_HANDLER = Callable[[RoleKey, str, str, LLMClient, str, ProgressCallback | None], Awaitable[None]]


class OrchestratorAgent:
    """
    负责给agent派活
    """

    def __init__(self):
        self._agent_handlers: dict[RoleKey, AGENT_HANDLER] = {
            "insight": insight_agent_handler,
            "media": media_agent_handler,
        }

    def dispatch_task(self, query: str, task_id: str):
        for role in self._agent_handlers:
            # 异步启动两个协程对象 并发执行
            research_task_manager.submit_task(self.execute_research_task(query, task_id, role))

    async def execute_research_task(self, query: str, task_id: str, role: RoleKey):
        """
        执行调查任务
        不需要返回值 ,落盘到var目录下
        """
        with route_log_by_role(role):
            self._publish_progress(
                task_id,
                role,
                ProgressUpdate(
                    status="starting",
                    message='开始执行研究',
                    progress_pct=0,
                ),
            )
            try:
                # 1. 获取角色对应的llm客户端
                llm_client = LLMClient.from_role(role)
                # 2. 获取角色对应的报告输出目录
                output_dir = get_output_dir(task_id, role)
                # 3. 执行执行角色Agent的逻辑
                await self._agent_handlers[role](
                    role,
                    query,
                    task_id,
                    llm_client,
                    output_dir,
                    lambda update:self._publish_progress(task_id,role,update)
                )
            except Exception as exc:
                logger.error(f"{role} 研究智能体执行期间出现异常: {exc}")
                publish_role_error(
                    RoleErrorEvent(
                        task_id=task_id,
                        role=role,
                        error=str(exc)
                    )
                )
                return
            publish_role_result(
                RoleResultEvent(
                    task_id=task_id,
                    role=role
                )
            )
    @staticmethod
    def _publish_progress(task_id:str,role:RoleKey,update:ProgressUpdate):
        publish_role_progress(
            RoleProgressEvent(
                task_id=task_id,
                role=role,
                status=update.status,
                message=update.message,
                progress_pct=update.progress_pct
            )
        )