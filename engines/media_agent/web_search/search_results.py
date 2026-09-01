from dataclasses import dataclass, field
from typing import Literal

SearchTool = Literal["comprehensive_search", "source_search", "realtime_search"]

SEARCH_TOOL_DESCRIPTIONS: dict[SearchTool, str] = {
    "comprehensive_search": (
        "不限近期和站点范围的综合检索，适合竞品官网/产品更新、公开案例、行业资料、"
        "长期商品口碑与多来源差异分析；优先用于“竞品动态与差异”，也可补充经营风险背景。"
    ),
    "source_search": (
        "限定主流电商平台官方域名的规则溯源检索，适合核验平台公告、规则中心、"
        "生效时间、处罚/履约/售后/结算规则；优先用于“平台规则变化与业务影响”。"
    ),
    "realtime_search": (
        "限定近一周公开社区与内容站点的时效检索，适合追踪商品口碑、商家公开反馈、"
        "争议变化和近期热点；优先用于“商家反馈与集中诉求”和“商品口碑与问题趋势”。"
    ),
}


@dataclass(frozen=True, slots=True)
class WebpageResult:
    title: str
    url: str
    content: str
    date: str
    score: float


@dataclass(frozen=True, slots=True)
class SearchProviderResponse:
    query: str
    webpages: list[WebpageResult] = field(default_factory=list)
