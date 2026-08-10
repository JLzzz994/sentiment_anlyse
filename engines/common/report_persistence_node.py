from typing import Any

from loguru import logger

from engines.common.reports import save_report
from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.agent_roles import ROLE_INFOS


class ReportPersistenceNode(ResearchNode):
    """将 Agent 独立报告落盘并注册到研究 运行"""

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        role = state['role']
        role_info = ROLE_INFOS[role]
        logger.info(f"{role_info.agent_name} 开始独立报告落盘")

        final_report = state['final_report']
        md_path = save_report(self.ctx.output_dir, f"{state['query']}_report_md", final_report)

        logger.info(f"{role_info.agent_name} 完成独立报告落盘: {md_path}")
        return {}
