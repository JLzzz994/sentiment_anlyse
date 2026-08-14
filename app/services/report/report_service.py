"""报告功能总协调器
Router -> ReportService -> ReportInputLoader -> ReportEngine
        _report_generations(内存状态)
"""
import uuid
from pathlib import Path
from typing import Any

from loguru import logger

from app.services.report.input_loader import ReportInputLoader, ReportInputStatus
from engines.common.task_manager import research_task_manager
from engines.report_engine.engine import ReportEngine
from engines.report_engine.models import ReportGeneration, ReportGenerationStatus, ReportInput, ReportOutput


class ReportService:
    """协调报告输入、异步生成状态、预览与下载"""

    def __init__(self):
        self._report_input_loader = ReportInputLoader()
        self._report_generations: dict[str, ReportGeneration] = {}
        self._report_engine = ReportEngine()

    def get_report_status(self, task_id: str) -> ReportInputStatus:
        """判断输入是否齐备"""
        return self._report_input_loader.get_report_input_status(task_id=task_id)

    def request_report_generation(self, task_id: str) -> ReportGeneration:
        """
        生成方法
        1. 检查三个输入文件
        2. 创建generation
        3.把协程交给统一任务管理器
        4. 立即返回generation 供前端拿generation_id轮询"""
        # 1. 检查三个输入文件
        input_status = self.get_report_status(task_id)
        if not input_status.prepared:
            raise RuntimeError("报告输入尚未就绪")
        # 2. 创建generation
        generation = self._prepare_report_generation(task_id, input_status.input_file_paths)
        # 3.把协程交给统一任务管理器
        research_task_manager.submit_task(
            self._run_report_generation(generation)
        )
        # 4. 立即返回generation 供前端拿generation_id轮询
        return generation

    def _prepare_report_generation(self, task_id: str, input_file_paths: dict[str, str]) -> ReportGeneration:
        """负责创建状态对象 并组织统一研究任务同时启动两份报告"""
        is_running = any(generation.task_id == task_id
                         and generation.status == ReportGenerationStatus.RUNNING
                         for generation in self._report_generations.values())

        if is_running:
            raise RuntimeError("当前研究任务已有报告正在生成")
        generation_id = f"generation_{uuid.uuid4().hex}"

        report_input: ReportInput = self._report_input_loader.load_report_input(
            generation_id=generation_id,
            task_id=task_id,
            file_paths=input_file_paths,
        )
        generation = ReportGeneration(report_input=report_input)
        self._report_generations[generation.generation_id] = generation
        return generation

    async def _run_report_generation(self, generation: ReportGeneration):
        """后台协程: 成功时complete() 异常时fail()"""
        try:
            report_output = await self._report_engine.generate_report(generation.report_input)
            generation.complete(report_output)
        except Exception as exc:
            logger.exception(f"报告生成失败:{exc}")
            generation.fail(str(exc))

    def get_completed_report_output(self,generation_id:str)->ReportOutput:
        """结果读取 :  生成记录不存在是LookupError 未完成和生成失败都是RuntimeError"""
        generation = self._report_generations.get(generation_id)

        if generation is None:
            raise LookupError("报告生成记录不存在")

        if generation.status == ReportGenerationStatus.ERROR:
            raise RuntimeError(
                f"报告生成失败: {generation.error_message}"
            )

        if generation.status != ReportGenerationStatus.COMPLETED:
            raise RuntimeError("报告尚未完成")
        return generation.report_output

    def get_download_file(
            self,
            generation_id:str,
            file_type:str,
    )->dict[str,Any]:
        report_output = self.get_completed_report_output(generation_id)
        if file_type == 'html':
            filepath = report_output.report_filepath
            filename = report_output.report_filename
            media_type = "text/html"
        elif file_type == 'md':
            filepath = report_output.markdown_filepath
            filename = report_output.markdown_filename
            media_type = "text/markdown"
        else:
            raise ValueError("不支持的报告文件类型")
        if not filepath or not Path(filepath).exists():
            raise LookupError("报告文件不存在或已被清理")
        return {
            "file_path":filepath,
            "file_name":filename,
            "media_type":media_type,
        }