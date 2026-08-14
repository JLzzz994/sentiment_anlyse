"""
事件总线收到事件 -> 找到相同task_id的队列 -> 放入JSON字符串
浏览器连上SSE -> 创建自己的队列 -> 持续yield队列消息
"""
import asyncio
import json
from loguru import logger

from engines.common.events import EventType, subscribe, unsubscribe


class ResearchProgressStream:
    """将研究进度事件转发给 按task_id 隔离的 SSE客户端"""
    FORWARDED_EVENT_TYPES = (
        EventType.ROLE_PROGRESS,
        EventType.ROLE_RESULT,
        EventType.ROLE_ERROR
    )

    def __init__(self):
        # 一个任务可被多个浏览器标签页订阅
        self._subscribers: dict[str, set[asyncio.Queue]] = {}

    def register_progress_update(self):
        """应用启动时注册到全局事件总线"""
        for event_type in self.FORWARDED_EVENT_TYPES:
            subscribe(event_type, self._broadcast_progress_update)

    def stop_progress_update(self):
        """关闭应用时移除订阅并清空队列"""
        unsubscribe(self._broadcast_progress_update)
        self._subscribers.clear()

    def _broadcast_progress_update(self, event_type: EventType, data: dict):
        """收到事件后，必须按 data["task_id"] 取队列集合。
        这样任务 A 的客户端不会收到任务 B 的进度"""
        payload = json.dumps({
            "event": event_type.value,
            "data": data
        },
            ensure_ascii=False
        )
        task_id = data['task_id']
        # 队列里放的是 JSON 字符串{事件类型和数据}
        for queue in list(self._subscribers.get(task_id, set())):
            queue.put_nowait(payload)

    async def stream_research_progress(self, request, task_id: str, ):
        """SSE 生成器。每一次浏览器连接，都必须创建一个独立队列"""
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.setdefault(task_id, set()).add(queue)
        logger.debug(f'SSE客户端连接: task_id={task_id}')
        try:
            yield {
                "event": "connected",
                "data": json.dumps({"status": "connected"}),
            }
            while True:
                if await request.is_disconnected():
                    break
                payload = await queue.get()
                yield {"data": payload}
        finally:
            task_subscribers = self._subscribers.get(task_id)
            if task_subscribers is not None:
                task_subscribers.discard(queue)
        logger.debug(f"SSE客户端关闭: task_id={task_id}")