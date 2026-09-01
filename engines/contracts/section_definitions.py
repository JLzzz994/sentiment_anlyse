"""电商规则与口碑研判平台：固定章节配置与私域证据路由规则。"""
from dataclasses import dataclass

from engines.contracts.agent_roles import RoleKey


@dataclass(slots=True)
class SectionDefinition:
    """固定章节标题、角色写作指导与私域路由关键词。"""

    key: str
    title: str
    insight_section_guidance: str
    media_section_guidance: str
    insight_routing_keywords: tuple[str, ...] = ()

    def section_guidance_for(self, role: RoleKey) -> str:
        if role == "insight":
            return self.insight_section_guidance
        if role == "media":
            return self.media_section_guidance
        raise ValueError(f"角色:{role}不支持章节写作指导")


SECTION_DEFINITIONS: dict[str, SectionDefinition] = {
    "platform_rule_changes": SectionDefinition(
        key="platform_rule_changes",
        title="平台规则变化与业务影响",
        insight_section_guidance=(
            "基于客服工单、商家反馈和历史问题案例，识别与平台规则、处罚、履约、售后、"
            "结算等变化相关的集中反馈；区分商家理解、历史经验与已确认规则事实。"
        ),
        media_section_guidance=(
            "优先检索电商平台官方规则、公告、规则中心和正式说明，梳理规则变化、"
            "生效时间、适用范围与明确影响；非官方解读只能作为补充，不得替代规则原文。"
        ),
        insight_routing_keywords=(
            "规则", "规则变更", "公告", "平台政策", "仅退款", "退款", "售后",
            "发货", "履约", "违规", "处罚", "保证金", "运费险", "结算",
            "淘宝", "天猫", "京东", "拼多多", "抖音电商", "快手电商",
        ),
    ),
    "merchant_feedback": SectionDefinition(
        key="merchant_feedback",
        title="商家反馈与集中诉求",
        insight_section_guidance=(
            "基于客服工单、商家反馈和历史问题案例归纳高频诉求、受影响业务环节、"
            "问题热度与重复出现模式；样本仅代表当前可见商家反馈，不外推为全部客户。"
        ),
        media_section_guidance=(
            "检索公开商家讨论、行业文章和平台相关问答，补充外部可见的经营诉求与争议；"
            "明确区分商家个案、行业观点和平台正式说明。"
        ),
        insight_routing_keywords=(
            "工单", "商家反馈", "客户反馈", "诉求", "投诉", "咨询", "使用问题",
            "操作问题", "订单", "库存", "仓储", "采购", "履约", "售后", "对账",
            "客服", "实施", "客户成功",
        ),
    ),
    "product_reputation": SectionDefinition(
        key="product_reputation",
        title="商品口碑与问题趋势",
        insight_section_guidance=(
            "基于商品评价、追评、售后反馈及相关工单，按商品和问题主题聚合正负向口碑、"
            "重复问题、近期变化与典型证据；不得用局部样本推断全量销量或总体满意度。"
        ),
        media_section_guidance=(
            "检索商品公开评价、社交平台讨论和媒体/测评内容，分析近期口碑主题、"
            "争议点与变化方向；缺少量化样本时不得推断全网占比。"
        ),
        insight_routing_keywords=(
            "商品", "SKU", "评价", "追评", "差评", "好评", "口碑", "质量",
            "尺码", "发货慢", "包装", "破损", "退货", "退款", "售后",
            "复购", "体验", "问题趋势",
        ),
    ),
    "competitor_dynamics": SectionDefinition(
        key="competitor_dynamics",
        title="竞品动态与差异",
        insight_section_guidance=(
            "基于商家反馈、历史问题案例和内部竞品记录，提炼客户明确提及的竞品能力、"
            "替代诉求与差异点；没有证据时不得推断竞品内部功能或经营数据。"
        ),
        media_section_guidance=(
            "检索竞品官网、产品更新、公开案例、公开评论与行业资料，比较功能、服务、"
            "规则适配和市场反馈差异；区分竞品官方主张与第三方评价。"
        ),
        insight_routing_keywords=(
            "竞品", "对比", "替代", "友商", "功能差异", "价格差异", "服务差异",
            "ERP", "WMS", "OMS", "聚水潭", "万里牛", "店小秘", "有赞", "金蝶",
            "功能需求", "迁移", "续费",
        ),
    ),
    "business_risk_opportunity": SectionDefinition(
        key="business_risk_opportunity",
        title="经营风险与机会研判",
        insight_section_guidance=(
            "综合私域反馈中的问题热度、重复出现、受影响对象和历史复现情况，识别产品、"
            "服务、履约、售后、规则适配等风险与潜在需求机会；明确事实与分析性判断边界。"
        ),
        media_section_guidance=(
            "综合平台规则、公开口碑、竞品动态和行业信息，识别可能放大或缓解商家经营影响的"
            "外部因素；不把相关性直接写成因果，不把公开评论直接写成商业结论。"
        ),
        insight_routing_keywords=(
            "风险", "机会", "影响", "损失", "增长", "下降", "集中问题", "高频",
            "严重", "优先级", "续费", "流失", "投诉升级", "经营", "履约风险",
            "售后风险", "规则适配", "产品机会", "需求机会",
        ),
    ),
}


def find_section_definition(key: str) -> SectionDefinition | None:
    return SECTION_DEFINITIONS.get(key)


def get_section_definitions_for_role(role: RoleKey) -> list[dict[str, str]]:
    return [
        {
            "section_key": section.key,
            "title": section.title,
            "section_guidance": section.section_guidance_for(role),
        }
        for section in SECTION_DEFINITIONS.values()
    ]


def get_insight_routing_rules() -> dict[str, tuple[str, ...]]:
    return {
        section.key: section.insight_routing_keywords
        for section in SECTION_DEFINITIONS.values()
    }
