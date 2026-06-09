# 插件契约测试 —— 所有注册的生产插件都必须满足 BasePlugin 协议
from __future__ import annotations

from spstpipe.core.base import BasePlugin
from spstpipe.core.registry import discover_plugins


def test_所有注册的插件都满足契约():
    plugins = discover_plugins(group="spstpipe.plugins")
    # Phase 3 完成后这里会 >= 6
    assert isinstance(plugins, dict)
    for name, cls in plugins.items():
        assert isinstance(cls, type), f"{name} 不是类"
        assert issubclass(cls, BasePlugin), f"{name} 不是 BasePlugin 子类"
        for m in ("load", "preprocess", "run", "save"):
            assert callable(getattr(cls, m, None)), f"{name} 缺方法 {m}"
        assert cls.name == name, f"key={name!r} 但 cls.name={cls.name!r}"