"""spstpipe - 空间转录组分析流水线核心包。

公开 API（自 1.0.0 起冻结，签名不再破坏性变化）：
  - __version__              : 当前包版本
  - __api_version__          : 冻结的 API 版本（1.0）
  - BasePlugin               : 插件抽象基类
  - discover_plugins(group)  : 通过 entry-point 发现插件

版本策略：PEP 440 语义化版本（major.minor.patch）。
"""

from __future__ import annotations

__version__ = "1.0.0"
__api_version__ = "1.0"
__all__ = ["BasePlugin", "__api_version__", "__version__", "discover_plugins"]

from spstpipe.core.base import BasePlugin
from spstpipe.core.registry import discover_plugins
