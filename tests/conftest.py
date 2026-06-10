"""pytest 全局配置 + Windows sandbox 适配。

Windows sandbox 下系统 Temp 经常不可写（sandbox 收紧 DACL），
导致 tmp_path fixture 的测试报 PermissionError。本文件在检测到这种情况时
自动 skip 那些依赖 tmp_path 的测试。CI / Linux 不受影响。
"""

from __future__ import annotations

import inspect
import sys
import tempfile
from pathlib import Path

import pytest

_SANDBOX_TEMP_BROKEN = False
if sys.platform == "win32":
    try:
        import getpass

        user = getpass.getuser()
        # pytest 9 tmp_path 用 pytest-of-{user} 子目录，必须测这个
        probe_dir = Path(tempfile.gettempdir()) / ("pytest-of-" + user)
        probe_dir.mkdir(parents=True, exist_ok=True)
        probe = probe_dir / ".sandbox_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError:
        _SANDBOX_TEMP_BROKEN = True


def _test_uses_tmp_path(func) -> bool:
    """检查测试函数是否用了 tmp_path fixture。"""
    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        return False
    return "tmp_path" in sig.parameters


def pytest_collection_modifyitems(config, items):
    """在收集阶段给 sandbox 下的 tmp_path 测试加 skip 标记。"""
    if not _SANDBOX_TEMP_BROKEN:
        return
    skip_marker = pytest.mark.skip(
        reason="sandbox 收紧 DACL，系统 Temp 不可写（CI / Linux 不受影响）"
    )
    for item in items:
        if _test_uses_tmp_path(item.function):
            item.add_marker(skip_marker)
