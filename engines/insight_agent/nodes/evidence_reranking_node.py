from typing import Any

from engines.common.research_graph_runtime import ResearchNode

"""
class ResearchNode(ABC):

    def __init__(self, ctx: ResearchRunContext):
        self.ctx = ctx

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:

"""
class EvidenceRerankingNode(ResearchNode):
    """合并重复召回证据并计算统一重排分"""

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """合并重复召回指标、计算排名分数并构建证据索引"""
        pass

