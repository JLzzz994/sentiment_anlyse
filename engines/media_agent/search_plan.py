from pydantic import BaseModel, Field

from engines.media_agent.web_search.search_results import SearchTool


class MediaSearchPlanItem(BaseModel):
    """llm 为单个固定章节生成的公域搜索策略"""
    search_tool:SearchTool=Field(
        description=(
            "从用户提供的可用搜索工具中为当前同索引章节选择一个工具;"
            "根据章节title、section_guidance和工具描述进行匹配,"
            "保留英文枚举值,不得假设工具具备描述之外的能力。"
        ),
    )
    search_keywords:list[str]=Field(
        min_length=1,
        max_length=3,
        description=(
            "当前同索引章节使用的1~3个中文补充查询关键词,单个查询关键词将形成一次独立搜索;"
            "应直接服务于章节证据需求并覆盖不同检索侧重点,不要重复研究问题,"
            "不要使用同义重复、宽泛空词、完整句号、标点符号、布尔运算符或说明文字。"
        ),
    )

class MediaSearchPlanOutput(BaseModel):
    """Media llm 搜索策略的顶层结构化输出"""
    sections: list[MediaSearchPlanItem] = Field(
        min_length=5,
        max_length=5,
        description=(
            "按用户提供的章节职责列表原始顺序生成的5项搜索计划;"
            "每项搜索计划按位置与输入章节一一对应：第1项对应第1个章节，第2项对应第2个章节；不得增删或重排。"
        )
    )