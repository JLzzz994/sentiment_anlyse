from typing import Any

from langgraph.constants import END
from langgraph.graph import StateGraph

from engines.common.agent_report_generation_node import AgentReportGenerationNode
from engines.common.llm import LLMClient
from engines.common.report_persistence_node import ReportPersistenceNode
from engines.common.research_graph_runtime import ResearchRunContext, route_after_section_summary, \
    SECTION_SUMMARY_LOOP_MAPPING

from engines.insight_agent.nodes.evidence_reranking_node import EvidenceRerankingNode
from engines.insight_agent.nodes.evidence_retrieval_node import EvidenceRetrievalNode
from engines.insight_agent.nodes.section_evidence_routing_node import SectionEvidenceRoutingNode
from engines.insight_agent.nodes.section_preparation_node import SectionPreparationNode
from engines.insight_agent.nodes.section_summary_node import SectionSummaryNode
from engines.insight_agent.state import InsightState


def build_graph(ctx: ResearchRunContext) -> Any:
    """构建并编译私域舆情智能体的LangGraph 工作流"""
    builder = StateGraph(InsightState)
    builder.add_node("retrieve_evidence", EvidenceRetrievalNode(ctx))
    builder.add_node("rerank_evidence", EvidenceRerankingNode(ctx))
    builder.add_node("route_section_evidence", SectionEvidenceRoutingNode(ctx))
    builder.add_node("prepare_sections", SectionPreparationNode(ctx))
    builder.add_node("summarize_sections", SectionSummaryNode(ctx))
    builder.add_node("generate_agent_report", AgentReportGenerationNode(ctx))
    builder.add_node("persist_agent_report", ReportPersistenceNode(ctx))
    builder.set_entry_point("retrieve_evidence")
    builder.add_edge("retrieve_evidence", "rerank_evidence")
    builder.add_edge("rerank_evidence", "route_section_evidence")
    builder.add_edge("route_section_evidence", "prepare_sections")
    builder.add_edge("prepare_sections", "summarize_sections")
    builder.add_conditional_edges(
        "summarize_sections",
        route_after_section_summary,
        SECTION_SUMMARY_LOOP_MAPPING,
    )
    builder.add_edge("generate_agent_report", "persist_agent_report")
    builder.add_edge("persist_agent_report", END)
    return builder.compile()


if __name__ == '__main__':
    graph = build_graph(ResearchRunContext(task_id="1", role="insight", llm_client=LLMClient.from_role("insight"),
                                           output_dir="/var/insight"))
    # 2. 静态测试  查看图的结构
    # 打印图结构
    # graph.get_graph().print_ascii()
