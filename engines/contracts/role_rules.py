from dataclasses import dataclass, Field, field
from typing import Literal

RoleKey = Literal['insight', 'media', 'host', 'report',]


@dataclass(slots=True)
class RoleInfo:
    config_prefix: str  # 角色配置前缀 用来辅助获取模型配置


ROLE_INFOS: dict[RoleKey, RoleInfo] = {
    "insight": RoleInfo(config_prefix='INSIGHT_ENGINE_'),
    "media": RoleInfo(config_prefix='MEDIA_ENGINE_'),
    "host": RoleInfo(config_prefix='HOST_'),
    "report": RoleInfo(config_prefix='REPORT_ENGINE_'),
}

