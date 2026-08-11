import json
from typing import Any

from langchain_core.prompts import PromptTemplate
from loguru import logger
from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.agent_roles import ROLE_INFOS
from engines.contracts.section_definitions import SECTION_DEFINITIONS, get_section_definitions_for_role
from engines.media_agent.search_plan import MediaSearchPlanOutput
from engines.media_agent.state import MediaState, MediaSectionState
from engines.media_agent.web_search.search_results import SEARCH_TOOL_DESCRIPTIONS
from engines.prompts.media import MEDIA_SEARCH_PLAN_USER_PROMPT, MEDIA_SEARCH_PLAN_SYSTEM_PROMPT


class SearchPlaningNode(ResearchNode):
    """为固定Media章节生成搜索工具与关键词"""

    async def __call__(self, state: MediaState) -> dict[str, Any]:
        """调用llm生成搜索策略,并与固定章节定义合并为运行状态"""
        role = state['role']
        role_info = ROLE_INFOS[role]
        logger.info(f"{role_info.agent_name} 开始规划公域搜索策略, 研究主题:{state['query']}")

        plan = await self._generate_search_plan(state['query'])

        sections: list[MediaSectionState] = [
            {
                "section_key": section_definition.key,
                "title": section_definition.title,
                "search_tool": plan_section.search_tool,
                "search_keywords": [keyword.strip() for keyword in plan_section.search_keywords],
            } for section_definition, plan_section in zip(SECTION_DEFINITIONS.values(), plan.sections)]

        logger.info(f"{role_info.agent_name} 完成规划公域搜索策略")
        return {"sections": sections}

    async def _generate_search_plan(self, research_topic:str,)->MediaSearchPlanOutput:
        """
        组装搜索规划提示词并调用llm返回结构化计划
        return :MediaSearchPlanOutput sections: list[MediaSearchPlanItem{search_tool:SearchTool,search_keywords:list[str]}]
        """
        # 工具名字和描述
        search_tools = [{"name":tool,"description":description} for tool,description in SEARCH_TOOL_DESCRIPTIONS.items()]
        prompt = PromptTemplate.from_template(MEDIA_SEARCH_PLAN_USER_PROMPT).format(
            research_topic=research_topic,
            section_contexts=json.dumps(
                get_section_definitions_for_role(self.ctx.role),
                ensure_ascii=False,
            ),
            search_tools=json.dumps(
                search_tools,
                ensure_ascii=False,
            ),
        )
        return await self.ctx.llm_client.generate_object(
            MEDIA_SEARCH_PLAN_SYSTEM_PROMPT,
            prompt,
            MediaSearchPlanOutput,
        )