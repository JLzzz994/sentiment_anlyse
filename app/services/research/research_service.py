from pathlib import Path

from app.services.research.research_cases import ECOMMERCE_RESEARCH_CASES

from engines.common.reports import get_output_dir
from engines.common.task_manager import research_task_manager, ResearchTask
from engines.contracts.agent_roles import RESEARCH_ROLE_KEYS
from engines.orchestrator import OrchestratorAgent


class ResearchService:
    """创建研究任务、派发Agent,并读取已落盘的角色报告"""
    def __init__(self):
        self._orchestrator = OrchestratorAgent()

    def research(self,query:str)->str:
        """创建研究任务、派发Agent"""
        research_task = research_task_manager.create_research_task(query)

        self._orchestrator.dispatch_task(query,research_task.task_id)
        return research_task.task_id

    def get_research_results(self,task_id:str)->tuple[str,dict[str,str]]:
        """
        return task_id, research_results role content
        """
        research_task:ResearchTask = research_task_manager.get_research_task(task_id)
        research_results:dict[str,str]={}

        for role in RESEARCH_ROLE_KEYS:
            report_file = (Path(get_output_dir(task_id,role)) / "report.md")

            if not report_file.exists():
                continue
            research_results[role]=report_file.read_text(
                encoding='utf-8',
                errors='ignore',
            )
        return research_task.task_id, research_results


    @staticmethod
    def get_research_examples() -> list[dict[str, object]]:
        """返回前端可直接展示和发起研究的 Demo Case。"""
        return [dict(case) for case in ECOMMERCE_RESEARCH_CASES]
