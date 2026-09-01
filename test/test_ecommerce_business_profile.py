from engines.contracts.agent_roles import role_display_name
from engines.contracts.judgement import SectionJudgement
from engines.contracts.section_definitions import SECTION_DEFINITIONS
from engines.media_agent.web_search.search_results import SEARCH_TOOL_DESCRIPTIONS


def test_business_sections_are_fixed_and_ordered():
    assert list(SECTION_DEFINITIONS) == [
        "platform_rule_changes",
        "merchant_feedback",
        "product_reputation",
        "competitor_dynamics",
        "business_risk_opportunity",
    ]


def test_agent_roles_match_ecommerce_workflow():
    assert "私域" in role_display_name("insight")
    assert "规则" in role_display_name("media")
    assert "风险机会" in role_display_name("host")
    assert "研判报告" in role_display_name("report")


def test_source_search_is_for_official_ecommerce_rules():
    description = SEARCH_TOOL_DESCRIPTIONS["source_search"]
    assert "电商平台官方" in description
    assert "规则" in description


def test_host_judgement_contains_business_actions():
    judgement = SectionJudgement(
        section_key="business_risk_opportunity",
        risk_signals=["退款风险上升"],
        opportunity_signals=["新增规则解释能力"],
        affected_objects=["售后团队"],
        recommended_actions=["补充规则知识库并回归高频工单"],
        evidence_review="证据可追溯",
        host_judgement="优先核验高频售后问题",
    )
    assert "建议动作" in judgement.content
    assert "补充规则知识库" in judgement.content
