import json
from pathlib import Path
from typing import Any
from loguru import logger
from app.services.host.discuss_buffer import DiscussionBuffer
from engines.common.events import subscribe, EventType, unsubscribe
from engines.host_agent.section_ready_listener import SectionReadyListener
from engines.common.reports import get_output_dir
from engines.contracts.section_definitions import SECTION_DEFINITIONS


class HostService:
    def __init__(self):
        self._listener = SectionReadyListener()
        self._discussion_buffer = DiscussionBuffer()

    def register_discussion_buffer(self):
        subscribe(EventType.HOST_DISCUSSION_MESSAGE,self._on_discussion_message)

    def stop_discussion_buffer(self):
        unsubscribe(self._on_discussion_message)


    def _on_discussion_message(self,_event_type:EventType,data:dict[str,Any]):
        logger.info(f"收到讨论消息...")
        self._discussion_buffer.append_message(data)

    def get_discussion_records(self,task_id:str)->dict[str,Any]:
        return self._discussion_buffer.read_messages(task_id=task_id)

    def register_host_listener(self):
        """注册并启动Host研判监听器"""
        self._listener.start()
        logger.info("HostService: 研判引擎启动成功")

    def stop_host_listener(self):
        """停止 Host 研判监听器"""
        self._listener.stop()
        logger.info("HostService: 研判引擎已停止")

    def get_judgements(self, task_id: str) -> dict[str, Any]:
        """读取 Host 已完成的五章结构化研判。"""
        path = Path(get_output_dir(task_id, "host")) / "judgements.json"
        if not path.exists():
            return {"task_id": task_id, "sections": []}
        judgements = json.loads(path.read_text(encoding="utf-8"))
        sections = []
        for judgement in judgements:
            definition = SECTION_DEFINITIONS.get(judgement.get("section_key"))
            sections.append({
                "title": definition.title if definition else judgement.get("section_key", ""),
                **judgement,
            })
        return {"task_id": task_id, "sections": sections}
