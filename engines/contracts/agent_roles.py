from dataclasses import dataclass
from typing import Literal

RoleKey = Literal['insight', 'media', 'host', 'report',]


@dataclass(slots=True)
class RoleInfo:
    config_prefix: str  # 角色配置前缀 用来辅助获取模型配置
    agent_name:str


ROLE_INFOS: dict[RoleKey, RoleInfo] = {
    "insight": RoleInfo(config_prefix='INSIGHT_ENGINE_',agent_name="私域检索智能体专家"),
    "media": RoleInfo(config_prefix='MEDIA_ENGINE_',agent_name="公域检索智能体专家"),
    "host": RoleInfo(config_prefix='HOST_',agent_name="研判智能体专家"),
    "report": RoleInfo(config_prefix='REPORT_ENGINE_',agent_name="报告引擎"),
}

