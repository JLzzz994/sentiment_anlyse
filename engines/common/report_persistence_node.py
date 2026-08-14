from typing import Any

from loguru import logger

from engines.common.reports import save_report
from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.agent_roles import ROLE_INFOS, role_display_name


class ReportPersistenceNode(ResearchNode):
    """将 Agent 独立报告落盘并注册到研究 运行"""

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        agent_name = role_display_name(state["role"])
        self.ctx.report_progress("completed", f"{agent_name} 开始保存独立报告", 90)
        final_report = state['final_report']
        md_path = save_report(self.ctx.output_dir, "report.md", final_report)
        self.ctx.report_progress("completed", f"{agent_name} 开始保存独立报告", 100)
        logger.info(f"{agent_name} 完成独立报告落盘: {md_path}")
        return {}
