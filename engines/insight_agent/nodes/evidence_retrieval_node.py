from typing import Any

from loguru import logger

from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.agent_roles import ROLE_INFOS
from engines.contracts.evidence import EvidenceRecord
from engines.insight_agent.tools.retrieval_service import InsightRetrievalService


class EvidenceRetrievalNode(ResearchNode):
    """调用私域召回服务获取尚未合并的原始证据"""

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """执行私域召回 并返回尚未合并的原始命中记录"""
        role = state['role']
        role_info = ROLE_INFOS[role]
        logger.info(f"{role_info.agent_name} 开始执行私域信息检索")
        evidence_records: list[EvidenceRecord] = await InsightRetrievalService().retrieval_evidence(state['query'])

        logger.info(f"{role_info.agent_name} 完成执行私域信息检索")
        return {"retrieved_records": evidence_records}
