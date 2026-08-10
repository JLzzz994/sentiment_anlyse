from engines.common.section_summary import BaseSectionSummaryNode
from engines.prompts.insight import INSIGHT_SECTION_SUMMARY_SYSTEM_PROMPT


class SectionSummaryNode(BaseSectionSummaryNode):
    """私域章节摘要节点: 基于证据包 生成各章节正文"""
    system_prompt = INSIGHT_SECTION_SUMMARY_SYSTEM_PROMPT
    max_rendered_evidence = 20
    FALLBACK_BODY="该章节未有相关内容,本章节不做任何延伸"
