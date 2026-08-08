from typing import Any

from engines.common.research_graph_runtime import ResearchNode


class EvidenceRetrievalNode(ResearchNode):
    """调用私域召回服务获取尚未合并的原始证据"""

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """执行私域召回 并返回尚未合并的原始命中记录"""
