from typing import Any

from engines.common.research_graph_runtime import ResearchNode


class ReportPersistenceNode(ResearchNode):
    """将 Agent 独立报告落盘并注册到研究 运行"""

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        pass
