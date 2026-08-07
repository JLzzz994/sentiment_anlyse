import asyncio
import inspect
from functools import wraps

from loguru import logger

class RetryConfig:
    max_retries: int = 3
    init_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0  # 回退因子

    def _get_delay(self, attempt: int) -> float:
        # 算重试时间间隔
        return min(self.init_delay * self.backoff_factor ** attempt, self.max_delay)

    def _is_no_retriable(self, exc: Exception) -> bool:
        # 第一次：直接拿 —— 适用于 httpx 等
        status_code = getattr(exc, 'status_code', None)
        # 第二次：往下钻一层 —— 适用于 requests/openai 等
        if status_code is None:
            status_code = getattr(getattr(exc, 'response', None), 'status_code', None)
        return isinstance(status_code, int) and 400 <= status_code < 500 and status_code != 429  # 429代表限流

    def get_retry_delay(self, func_name: str, attempt: int, exc: Exception) -> float | None:
        """
        获取尝试延迟
        """
        # 1. 不能重试或者重试次数耗尽
        if self._is_no_retriable(exc) or attempt >= self.max_retries:
            return None
        delay = self._get_delay(attempt)
        current_try = attempt + 1
        next_try = current_try + 1
        logger.warning(f"{func_name}函数执行失败，正在第{current_try}次重试，请稍候，预计{delay}秒后重试，请勿关闭程序")
        logger.info(f"将在{delay:.1f}秒后进行第{next_try}次重试...")

        return delay


retry_config = RetryConfig()


async def with_retry(func):
    """
    异步重试 装饰器
    """

    if not inspect.iscoroutinefunction(func):
        raise TypeError(
            "重试装饰器只能装饰async函数,"
            f"得到的是同步函数{func.__name__}"
        )
    @wraps(func) # ← 把 func 的元信息复制给 wrapper
    async def wrapper(*args, **kwargs):
        for attempt in range(retry_config.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                delay = retry_config.get_retry_delay(func.__name__,attempt,e)
                if delay is None:
                    raise
                await asyncio.sleep(delay)
    return wrapper
