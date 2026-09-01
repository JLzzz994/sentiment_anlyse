"""Insight|Media 共享的章节摘要节点基类"""
from typing import Any

from langchain_core.prompts import PromptTemplate
from loguru import logger

from engines.common.events import publish_section_ready
from engines.common.evidence_persistence import persist_section_evidence
from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.agent_roles import ROLE_INFOS, role_display_name
from engines.contracts.evidence import build_evidence_context, EvidenceRecord, EvidenceContext
from engines.contracts.research_graph_state import SectionState
from engines.contracts.section_definitions import find_section_definition
from engines.prompts.shared import SECTION_SUMMARY_USER_PROMPT


class BaseSectionSummaryNode(ResearchNode):
    """章节摘要节点基类: 游标推进 证据组装 llm 生成摘要 和 事件发布"""

    system_prompt: str = ""
    user_prompt_template: str = SECTION_SUMMARY_USER_PROMPT
    max_rendered_evidence: int = 10
    fallback_body: str = ""

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """按游标取证据包生成章节正文 并发布就绪事件"""
        cursor = state.get("cursor", 0)
        agent_name = role_display_name(state["role"])
        self.ctx.report_progress("summary", f"{agent_name} 开始按游标:{cursor}生成章节摘要", 50)


        sections = list(state.get("sections"))
        if cursor >= len(sections):
            return {"sections": sections}
        """
        class SectionState(TypedDict):
           完成规划后在研究图中持续传递的章节状态
            section_key: str
            title: str
            body: NotRequired[str] # 暂时不需要定义 章节摘要
        """
        section = sections[cursor]

        section_records:list[EvidenceRecord] = self._section_records(state, cursor)
        retrieval_text = self._retrieval_text(state, cursor)
        persist_section_evidence(
            output_dir=self.ctx.output_dir,
            task_id=state["task_id"],
            role=state["role"],
            section_key=section["section_key"],
            section_title=section["title"],
            retrieval_text=retrieval_text,
            records=section_records,
            rerank_scores=state.get("rerank_scores"),
        )
        if not section_records:
            logger.info(f"章节 {section.get('section_key')} 证据上下文为空,跳过生成")
        else:
            evidence_context = build_evidence_context(
                retrieval_text=retrieval_text,
                records=section_records,
                max_rendered=self.max_rendered_evidence,
            )
            section["body"] = await self._generate_section_body(
                state,
                section,
                evidence_context,
            )
        # todo 发布摘要生成事件给HostAgent 做章节研判
        publish_section_ready(state,section)

        sections[cursor] = section

        self.ctx.report_progress("summary", f"{agent_name} 完成按游标:{cursor}生成章节摘要", 60)

        return {"sections": sections, "cursor": cursor + 1}

    def _section_records(self, state:dict[str,Any], cursor:int)->list[EvidenceRecord]:
        """取当前游标对应章节的 证据记录 , 无值返回空列表"""
        section_records =state.get("section_evidence_records")
        return section_records[cursor]

    def _retrieval_text(self, state:dict[str,Any],cursor:int)->str:
        """章节证据对应的检索文本, 默认取研究主题"""
        return state['query']

    async def _generate_section_body(self, state:dict[str,Any], section:SectionState, evidence_context:EvidenceContext)->str:
        """调用llm生成章节正文 并清洗 Markdown"""
        section_key = section["section_key"]
        section_definition = find_section_definition(section_key)
        # 每次调用该节点的章节都不一样,所以需要用章节key来定位, 得到章节职责section_context
        section_context = {
            "section_key": section_key, # 章节key
            "title":section.get("title"), # 章节标题
            "section_guidance":section_definition.section_guidance_for(state['role']),# 章节指导
        }
        user_prompt = PromptTemplate.from_template(template=self.user_prompt_template).format(
            section_context=section_context, # 章节key 标题 指导
            retrieval_text= evidence_context.retrieval_text, #实际检索请求
            evidence_text = evidence_context.evidence_text #证据材料 EvidenceRecord转成str
        )
        body = await self.ctx.llm_client.generate_text(self.system_prompt,user_prompt)
        return body