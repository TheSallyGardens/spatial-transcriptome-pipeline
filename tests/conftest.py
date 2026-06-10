"""pytest 全局配置。

Windows sandbox 环境（Codex/沙箱用户）下，系统 Temp 可能不可写。
本文件在 Windows + sandbox 时把 TMP/TEMP 临时改写到 D:\project\pytest_basetemp。
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path


def _maybe_redirect_temp() -> None:
    """在 Windows sandbox 环境下，把系统 Temp 重定向到可写位置。"""
    if sys.platform != "win32":
        return
    system_temp = Path(tempfile.gettempdir())
    test_path = system_temp / ".sandbox_write_probe"
    try:
        test_path.write_text("ok", encoding="utf-8")
        test_path.unlink()
    except OSError:
        # 系统 Temp 不可写（sandbox 收紧），切到 D:\project\pytest_basetemp
        alt = Path("D:/project/pytest_basetemp")
        alt.mkdir(parents=True, exist_ok=True)
        os.environ["TEMP"] = str(alt)
        os.environ["TMP"] = str(alt)
        tempfile.tempdir = str(alt)


_maybe_redirect_temp()