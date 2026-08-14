import json

from langchain_core.prompts import PromptTemplate
from loguru import logger

from engines.common.llm import LLMClient
from engines.common.reports import get_output_dir, save_report
from engines.contracts.section_definitions import SECTION_DEFINITIONS
from engines.prompts.report import (
    FINAL_REPORT_GENERATION_SYSTEM_PROMPT,
    FINAL_REPORT_GENERATION_USER_PROMPT,
)
from engines.report_engine.models import ReportInput, ReportOutput
from engines.report_engine.renderer import render_html, render_markdown


class ReportEngine:
    """报告生成引擎: 负责驱动llm 生成Markdown报告、渲染html并落盘
    ReportInput
  → 组装 Prompt
  → LLM 输出 Markdown
  → Mistune 转 HTML
  → 分别保存 .md / .html
  → ReportOutput
    """

    def __init__(self):
        """初始化报告引擎并绑定llm客户端"""
        # 1. 实例化专门用于报告生成的llm客户端
        self._llm_client = LLMClient.from_role("report")

    async def generate_report(self, report_input: ReportInput) -> ReportOutput:
        """完整综合报告生成的工作流: 生成Markdown报告、渲染html并保存文件"""
        # 1. 以Host 研判为结论依据, 结合双Agent报告生成最终Markdown
        markdown = await self._generate_markdown(report_input)

        # 2. 将Markdown 渲染为HTML 格式文本
        html = render_html(render_markdown(markdown), report_input.query)

        # 3. 将生成的Markdown 和HTML 文件保存到本地磁盘并返回元数据
        return self._save_final_report(
            report_input.task_id,
            report_input.generation_id,
            markdown,
            html
        )

    async def _generate_markdown(self, report_input: ReportInput) -> str:
        """根据结构化Host研判和双Agent 报告生成最终Markdown"""
        # 1. 提取固定章节定义, 构建最终报告的章节上下文
        section_contexts = [{
            "section_key":section.key,
            "title": section.title
        } for section in SECTION_DEFINITIONS.values()]
        # 2. 将Host 章节研判转换为可序列化数据
        host_judgements=[judgement.model_dump() for judgement in report_input.host_judgements]
        # 3. 将章节上下文和Host 研判序列化为提示词所需的JSON
        section_contexts_json = json.dumps(section_contexts,ensure_ascii=False,indent=2)
        host_judgements_json = json.dumps(host_judgements,ensure_ascii=False,indent=2)

        # 4. 结合研究主题、结构化上下文和双Agent 原始报告构建用户提示词
        user_prompt_template = PromptTemplate.from_template(FINAL_REPORT_GENERATION_USER_PROMPT)
        user_prompt = user_prompt_template.format(
            research_topic=report_input.query,
            section_contexts=section_contexts_json,
            host_judgements=host_judgements_json,
            insight_report=report_input.insight_report,
            media_report=report_input.media_report
        )
        # 5. 调用报告角色 LLM 生成最终 Markdown
        return await self._llm_client.generate_text(FINAL_REPORT_GENERATION_SYSTEM_PROMPT,user_prompt,)

    def _save_final_report(
        self, task_id: str, generation_id: str, markdown: str, html: str
    ) -> ReportOutput:
        """保存最终Markdown 与HTML 报告"""
        report_dir = get_output_dir(task_id,"report")
        markdown_path = save_report(report_dir,f"{generation_id}.md",markdown)
        html_path = save_report(report_dir,f"{generation_id}.html",html)
        logger.info(f"报告已落盘: {html_path}")
        return ReportOutput(
            html_content=html,
            markdown_filepath=str(markdown_path),
            markdown_filename=markdown_path.name,
            report_filepath=str(html_path),
            report_filename=html_path.name

        )