from typing import Any

from langgraph.constants import END
from langgraph.graph import StateGraph

from engines.common.agent_report_generation_node import AgentReportGenerationNode
from engines.common.report_persistence_node import ReportPersistenceNode
from engines.common.research_graph_runtime import ResearchRunContext, route_after_section_summary, \
    SECTION_SUMMARY_LOOP_MAPPING
from engines.media_agent.nodes.search_planing_node import SearchPlaningNode
from engines.media_agent.nodes.section_search_node import SectionSearchNode
from engines.media_agent.nodes.section_summary_node import SectionSummaryNode
from engines.media_agent.state import MediaState


def build_graph(ctx:ResearchRunContext)->Any:
    """编排规划、检索、摘要、排版、落盘"""
    builder = StateGraph(MediaState)
    builder.add_node("plan_search",SearchPlaningNode(ctx))
    builder.add_node("search",SectionSearchNode(ctx))
    builder.add_node("summarize_sections",SectionSummaryNode(ctx))
    builder.add_node("generate_agent_report",AgentReportGenerationNode(ctx))
    builder.add_node("persist_agent_report",ReportPersistenceNode(ctx))
    builder.set_entry_point("plan_search")
    builder.add_edge("plan_search",'search')
    builder.add_edge("search",'summarize_sections')
    builder.add_conditional_edges(
        "summarize_sections",
        route_after_section_summary,
        SECTION_SUMMARY_LOOP_MAPPING,
    )


    builder.add_edge("generate_agent_report",'persist_agent_report')
    builder.add_edge("persist_agent_report",END)
    return builder.compile()
