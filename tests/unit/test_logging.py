"""日志初始化的测试。"""
from __future__ import annotations

from spstpipe.core.logging import setup


def test_setup_幂等_返回同一_logger():
    """多次 setup 应该返回同一个 logger 句柄。"""
    a = setup()
    b = setup()
    assert a is b


def test_setup_不抛异常():
    """默认参数应该能正常初始化。"""
    log = setup(level="INFO")
    assert log is not None