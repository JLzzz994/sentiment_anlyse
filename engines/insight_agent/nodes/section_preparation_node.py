from typing import Any

from engines.common.research_graph_runtime import ResearchNode


class SectionPreparationNode(ResearchNode):
    """初始化固定章节并为各章节选择、排序和截取证据"""

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """生成固定章节状态及供摘要节点消费的章节证据列表"""
        pass
