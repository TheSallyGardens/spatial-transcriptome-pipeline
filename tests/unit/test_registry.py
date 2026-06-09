"""插件注册表的测试。"""
from __future__ import annotations

from spstpipe.core.base import BasePlugin
from spstpipe.core.registry import discover_plugins


def test_注册表_能发现_test_plugins_组的假插件():
    """discover_plugins 应该能从 entry-point 找到 SyntheticPlugin。"""
    plugins = discover_plugins(group="spstpipe.test_plugins")
    assert "synthetic" in plugins
    cls = plugins["synthetic"]
    assert issubclass(cls, BasePlugin)
    assert cls.name == "synthetic"


def test_注册表_对不存在的组_返回空字典():
    """不存在的 entry-point 组应该返回空字典，不抛错。"""
    plugins = discover_plugins(group="spstpipe.不存在的组_xyz")
    assert plugins == {}


def test_注册表_返回的插件_都能拿到_name():
    """发现出来的每个插件类都应该有非空 name。"""
    plugins = discover_plugins(group="spstpipe.test_plugins")
    for name, cls in plugins.items():
        assert name == cls.name, f"key={name!r} 但 cls.name={cls.name!r}"