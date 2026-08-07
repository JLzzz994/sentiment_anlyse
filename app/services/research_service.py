from engines.common.task_manager import research_task_manager
from engines.orchestrator import OrchestratorAgent


class ResearchService:
    def __init__(self):
        self._orchestrator = OrchestratorAgent()

    def research(self, query: str) -> str:
        """
        路由层调用该方法 返回task_id
        """
        # 1. 创建一次查询话题的任务
        research_task = research_task_manager.create_research_task(query)
        # 2. 编排器 转发查询话题的任务 给两个Agent去使用
        self._orchestrator.dispatch_task(query, research_task.task_id)
        # 3. 将本次查询的话题任务id 返回(路由层需要->前端需要->前端轮询查询任务是否完成)
        return research_task.task_id
