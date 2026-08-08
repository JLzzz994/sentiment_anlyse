import os
from contextlib import contextmanager
from pathlib import Path

from loguru import logger

from engines.contracts.agent_roles import RoleKey
from engines.contracts.settings import get_settings


@contextmanager
def route_log_by_role(role: RoleKey):
    """
    根据Agent的角色分发日志
    :param role:
    :return:
    """
    log_handler_id = None
    settings = get_settings()
    log_dir = Path(settings.LOG_DIR)
    with logger.contextualize(role=role):  # 给日志对象添加一个固定的上下文 extra:{"role":role }
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            log_handler_id = logger.add(
                sink=log_dir / f"{role}.log",
                level='INFO',
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | [{extra[role]}] | {name} | {message}",
                rotation="1 MB",
                encoding='utf-8',
                filter=lambda record: record['extra'].get('role') == role
            )
            yield  # yield之后执行真正使用时 with route_log_by_role('report'): xxx()
        finally:
            if log_handler_id:
                logger.remove(log_handler_id)
