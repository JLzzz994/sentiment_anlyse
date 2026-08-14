from enum import Enum
from typing import Literal, Callable, Any, Mapping, Set

from loguru import logger
from pydantic import BaseModel

from engines.contracts.agent_roles import role_display_name


class EventType(str, Enum):
    """研究流程中可发布的事件类型"""
    ROLE_PROGRESS = "role_progress"
    ROLE_ERROR = "role_error"
    ROLE_RESULT = "role_result"
    SECTION_READY = "section_ready"
    HOST_DISCUSSION_MESSAGE = 'host_discussion_message'


class SectionReadyEvent(BaseModel):
    """章节准备事件"""
    task_id: str  # 任务id
    source: str  # 角色
    section_key: str  # 章节key
    body: str  # 章节摘要


class HostDiscussionMessageEvent(BaseModel):
    """主持讨论消息事件"""
    task_id: str  # 任务id
    source: Literal['insight', 'media', 'host']  # 角色
    section_key: str  # 章节key
    content: str  # 讨论内容 两个摘要 一个研判总结

class RoleProgressEvent(BaseModel):
    task_id:str
    role:str
    status:str
    message:str
    progress_pct:int = 0

class RoleResultEvent(BaseModel):
    task_id:str
    role:str

class RoleErrorEvent(BaseModel):
    task_id:str
    role:str
    error:str

# 定义 订阅者的事件回调函数满足的要求 输出是 EventType, dict[str, Any] 输出为None 的函数
EventCallback = Callable[[EventType, dict[str, Any]], None]
# 定义字典 key是事件类型 value 是事件回调函数的集合 作用1.相同回调函数只注册一次
_subscribers: dict[EventType, Set[EventCallback]] = {}


def subscribe(event_type: EventType, callback: EventCallback):
    _subscribers.setdefault(event_type, set()).add(callback)


def publish(event_type: EventType, data: dict[str, Any]):
   for callback in _subscribers.get(event_type,set()):
       try:
           callback(event_type,data)
       except Exception as e:
           logger.error(f"事件订阅者执行失败: {e}")

def unsubscribe(callback:EventCallback):
    for subscribers in _subscribers.values():
        subscribers.discard(callback)

def publish_section_ready(state:Mapping[str,Any],section:Mapping[str,Any]):
    """从研究Agent图状态中 构造并发布章节就绪事件"""
    role = state['role']
    agent_name = role_display_name(role)
    event = SectionReadyEvent(
        task_id=state['task_id'],
        source=role,
        section_key=section['section_key'],
        body=section.get('body', '')
    )
    #model_dump 对象转为字典
    publish(EventType.SECTION_READY,event.model_dump())
    logger.info(f"[{agent_name}] 发布 [章节{event.section_key}]事件")

def publish_host_discussion_message(event:HostDiscussionMessageEvent):
    publish(EventType.HOST_DISCUSSION_MESSAGE,event.model_dump())

# 语义化发布
def publish_role_progress(event:RoleProgressEvent):
    publish(EventType.ROLE_PROGRESS,event.model_dump())

def publish_role_result(event:RoleResultEvent):
    publish(EventType.ROLE_RESULT,event.model_dump())

def publish_role_error(event:RoleErrorEvent):
    publish(EventType.ROLE_ERROR,event.model_dump())
    