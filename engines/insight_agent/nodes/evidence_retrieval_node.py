from typing import Any

from loguru import logger

from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.agent_roles import ROLE_INFOS, role_display_name
from engines.contracts.evidence import EvidenceRecord
from engines.insight_agent.tools.retrieval_service import InsightRetrievalService


class EvidenceRetrievalNode(ResearchNode):
    """调用私域召回服务获取尚未合并的原始证据"""

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """执行私域召回 并返回尚未合并的原始命中记录"""
        agent_name = role_display_name(state['role'])
        self.ctx.report_progress("searching", f"{agent_name} 开始执行私域信息检索", 10)

        evidence_records: list[EvidenceRecord] = await InsightRetrievalService().retrieval_evidence(state['query'])

        self.ctx.report_progress("searching", f"{agent_name} 完成执行私域信息检索", 20)
        return {"retrieved_records": evidence_records}
