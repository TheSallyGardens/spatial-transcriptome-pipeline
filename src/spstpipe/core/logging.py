# loguru 日志初始化 —— 配置一次、到处使用。
#
# setup() 多次调用是幂等的（返回同一个 logger 句柄）。level 接受字符串
# "DEBUG"/"INFO"/"WARNING"/"ERROR" 之一。json=True 时输出 JSON 行（给 CI 用）。
from __future__ import annotations

import sys
from typing import Any, Literal

from loguru import logger

_setup_done = False


def setup(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO",
    json: bool = False,
) -> Any:
    global _setup_done
    if not _setup_done:
        logger.remove()
        if json:
            logger.add(sys.stderr, serialize=True, level=level)
        else:
            logger.add(
                sys.stderr,
                level=level,
                format="<green>{time:HH:mm:ss}</green> | <level>{level: <7}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            )
        _setup_done = True
    return logger
