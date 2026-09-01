from dataclasses import dataclass
from typing import Literal

RoleKey = Literal["insight", "media", "host", "report"]


@dataclass(slots=True)
class RoleInfo:
    config_prefix: str
    agent_name: str


ROLE_INFOS: dict[RoleKey, RoleInfo] = {
    "insight": RoleInfo(
        config_prefix="INSIGHT_ENGINE_",
        agent_name="商家私域反馈研究 Agent",
    ),
    "media": RoleInfo(
        config_prefix="MEDIA_ENGINE_",
        agent_name="平台规则与口碑公域研究 Agent",
    ),
    "host": RoleInfo(
        config_prefix="HOST_",
        agent_name="跨来源风险机会研判 Agent",
    ),
    "report": RoleInfo(
        config_prefix="REPORT_ENGINE_",
        agent_name="电商研判报告 Agent",
    ),
}


def role_display_name(role_key: RoleKey) -> str:
    return ROLE_INFOS[role_key].agent_name


RESEARCH_ROLE_KEYS: tuple[RoleKey, ...] = ("insight", "media")
