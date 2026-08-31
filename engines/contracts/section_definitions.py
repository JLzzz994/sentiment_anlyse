"""固定报告的章节配置与检索路由规则"""
from dataclasses import dataclass

from engines.contracts.agent_roles import RoleKey


@dataclass(slots=True)
class SectionDefinition:
    """固定的章节标题、角色写作指导与私域路由关键词"""

    key: str
    title: str
    insight_section_guidance: str  # 私域章节指导
    media_section_guidance: str  # 公域章节指导
    insight_routing_keywords: tuple[str, ...] = ()

    def section_guidance_for(self, role: RoleKey) -> str:
        """返回研究角色对应的章节写作指导"""
        if role == "insight":
            return self.insight_section_guidance
        if role == "media":
            return self.media_section_guidance
        raise ValueError(f"角色:{role}不支持章节写作指导")


SECTION_DEFINITIONS: dict[str, SectionDefinition] = {
    "background_overview": SectionDefinition(
        key="background_overview",
        title="规则变化与事件概览",
        insight_section_guidance=(
            "基于当前可见的客服工单、商家反馈、实施记录和历史异常案例，梳理问题首次出现时间、"
            "涉及业务链路和内部已知现象；仅概括材料中明确陈述的信息，不把单个商家反馈视为普遍事实。"
        ),
        media_section_guidance=(
            "基于平台官方公告、规则文档和公开行业信息，梳理规则调整背景、生效时间、适用范围和关键变化；"
            "区分官方直接陈述、行业媒体解读与尚未核实的信息。"
        ),
        insight_routing_keywords=(
            "规则", "公告", "通知", "调整", "变更", "生效", "升级", "接口",
            "字段", "订单", "退款", "售后", "库存", "物流", "活动",
        ),
    ),
    "heat_and_spread": SectionDefinition(
        key="heat_and_spread",
        title="影响范围与问题热度",
        insight_section_guidance=(
            "结合工单数量、商家反馈频次、订单/SKU/店铺影响描述及问题热度分，分析问题是否集中出现、"
            "影响哪些业务链路；不同数据来源口径不一致时避免直接比较绝对数值。"
        ),
        media_section_guidance=(
            "梳理公开信息中可识别的适用平台、类目、商家范围、发布时间和行业关注度；"
            "缺少量化数据时不推断实际受影响商家规模。"
        ),
        insight_routing_keywords=(
            "集中反馈", "批量", "影响", "异常", "工单", "投诉", "失败", "超时",
            "同步", "积压", "频发", "高发", "商家数", "订单量", "SKU", "店铺",
        ),
    ),
    "sentiment_and_opinion": SectionDefinition(
        key="sentiment_and_opinion",
        title="商家反馈与核心诉求",
        insight_section_guidance=(
            "提炼客服工单、商家反馈和实施记录中的主要问题表现、业务诉求与重复出现的痛点，"
            "区分事实描述、用户主观判断和处理建议，不将当前样本外推为全部商家意见。"
        ),
        media_section_guidance=(
            "分析公开规则解读、行业讨论和平台答疑中与商家执行相关的重点关注项，"
            "区分平台规则原文、媒体/从业者解读与个体经验。"
        ),
        insight_routing_keywords=(
            "反馈", "诉求", "抱怨", "质疑", "不满", "担忧", "希望", "建议",
            "咨询", "催促", "人工", "赔付", "退款", "库存", "发货", "售后",
        ),
    ),
    "platform_and_group_diff": SectionDefinition(
        key="platform_and_group_diff",
        title="平台与商家类型差异",
        insight_section_guidance=(
            "比较不同平台、商家规模、业务版本、类目或业务链路下的问题表现和处理差异；"
            "任一分组样本不足时明确说明，不推断缺乏证据支持的商家画像。"
        ),
        media_section_guidance=(
            "比较不同电商平台的规则口径、适用范围、时间节点和执行要求，"
            "并说明不同来源的比较范围与证据限制。"
        ),
        insight_routing_keywords=(
            "淘宝", "天猫", "京东", "抖音", "拼多多", "快手", "小红书", "跨境",
            "大商家", "中小商家", "品牌", "店铺", "类目", "版本", "区域", "渠道",
        ),
    ),
    "deep_causes_and_impact": SectionDefinition(
        key="deep_causes_and_impact",
        title="经营影响与风险研判",
        insight_section_guidance=(
            "基于内部问题记录分析潜在根因、受影响业务链路和后续经营风险，重点关注订单、库存、"
            "履约、售后、资金与人效影响；区分材料陈述、用户归因与分析性推断。"
        ),
        media_section_guidance=(
            "基于平台官方规则和公开行业信息分析规则变化可能带来的经营影响、执行风险与关注事项，"
            "区分信源结论与分析推断，避免将相关性表述为已确认因果关系。"
        ),
        insight_routing_keywords=(
            "经营风险", "订单", "库存", "履约", "退款", "售后", "资金", "结算",
            "流量", "转化", "成本", "人效", "合规", "稳定性", "原因", "根因",
            "应对", "优先级",
        ),
    ),
}


def find_section_definition(key: str) -> SectionDefinition | None:
    """按键名查找固定章节定义，未知键返回None"""
    return SECTION_DEFINITIONS.get(key)


def get_section_definitions_for_role(role: RoleKey) -> list[dict[str, str]]:
    """返回指定研究角色的固定章节与规划指导"""
    return [
        {
            "section_key": section.key,
            "title": section.title,
            "section_guidance": section.section_guidance_for(role),
        }
        for section in SECTION_DEFINITIONS.values()
    ]


def get_insight_routing_rules() -> dict[str, tuple[str, ...]]:
    """提取五个章节的私域证据路由关键词"""
    return {
        section.key: section.insight_routing_keywords
        for section in SECTION_DEFINITIONS.values()
    }
