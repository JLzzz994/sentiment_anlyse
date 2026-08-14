from typing import Any

from langgraph.constants import END
from langgraph.graph import StateGraph

from engines.host_agent.nodes import HostNodes
from engines.host_agent.section_judge import HostSectionJudge
from engines.host_agent.state import HostState


def _route_after_judgement(state:HostState)->str:
    """全部章节研判完成时保存结构化结果,否则等待后续事件"""
    return "save" if state["section_pair_store"].all_sections_judged() else "waiting"


def _route_after_output_collection(state:HostState)->str:
    """章节配对齐备时进入生成研判,否则结束本次事件处理"""
    return "ready" if state["section_pair_store"].has_ready_pair() else "waiting"



def build_graph(section_judge:HostSectionJudge)->Any:
    """构建并编译Host章节研判LangGraph"""
    nodes = HostNodes(section_judge)
    builder = StateGraph(HostState)
    builder.add_node("collect_agent_output",nodes.collect_agent_output)
    builder.add_node("generate_section_judgement",nodes.generate_section_judgement)
    builder.add_node("apply_section_judgement",nodes.apply_section_judgement)
    builder.add_node("save_judgements",nodes.save_judgements)

    builder.set_entry_point('collect_agent_output')
    builder.add_conditional_edges(
        'collect_agent_output',
        _route_after_output_collection,
        {
            "ready": "generate_section_judgement",
            "waiting":END,
        },
    )
    builder.add_edge('generate_section_judgement','apply_section_judgement')
    builder.add_conditional_edges(
        'apply_section_judgement',
        _route_after_judgement,
        {
            "save":"save_judgements",
            "waiting":END,
        }
    )
    builder.add_edge("save_judgements",END)
    return builder.compile()