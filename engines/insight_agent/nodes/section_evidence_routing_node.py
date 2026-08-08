from typing import Any

from engines.common.research_graph_runtime import ResearchNode


class SectionEvidenceRoutingNode(ResearchNode):
    """将重排证据按规则或语义相似度路由到固定章节"""

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        pass
    
