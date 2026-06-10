"""BasePlugin 抽象类的测试。"""

from __future__ import annotations

from abc import ABC

import anndata as ad
import numpy as np
import pytest

import spstpipe
from spstpipe.core.base import BasePlugin


def test_BasePlugin_是_ABC_的子类():
    """BasePlugin 必须继承自 ABC，强制子类实现四个方法。"""
    assert issubclass(BasePlugin, ABC)


def test_BasePlugin_有_四个抽象方法():
    """load / preprocess / run / save 四个方法必须存在。"""
    for name in ("load", "preprocess", "run", "save"):
        assert hasattr(BasePlugin, name), f"BasePlugin 缺少 {name}"


def test_BasePlugin_不能直接实例化():
    """抽象类不能被实例化。"""
    with pytest.raises(TypeError):
        BasePlugin()  # type: ignore[abstract]


def test_BasePlugin_子类_必须实现所有抽象方法():
    """只实现部分抽象方法的子类应该还是抽象的。"""

    class 半成品(BasePlugin):
        def load(self, paths):
            return None  # type: ignore[return-value]

    with pytest.raises(TypeError):
        半成品()  # type: ignore[abstract]


def test_BasePlugin_完整子类_可以实例化_并_调用_call():
    """完整子类的实例能直接被调用，相当于 run(adata)。"""

    captured: list[ad.AnnData] = []

    class 假插件(BasePlugin):
        name = "fake"
        version = "0.0.1"

        def load(self, paths):
            return ad.AnnData(np.zeros((0, 0)))

        def preprocess(self, adata):
            return adata

        def run(self, adata):
            captured.append(adata)
            adata.obs["marker"] = "yes"
            return adata

        def save(self, adata, path):
            pass

    a = ad.AnnData(np.zeros((3, 2)))
    p = 假插件()
    out = p(a)
    assert captured == [a]
    assert out.obs["marker"].iloc[0] == "yes"
    assert 假插件.name == "fake"


def test_spstpipe_version_已发布_1_0():
    import spstpipe

    assert spstpipe.__version__ == "1.0.0"
    assert spstpipe.__api_version__ == "1.0"


def test_spstpipe_公开API_可导入():
    from spstpipe import BasePlugin as BP1
    from spstpipe import discover_plugins as DP1
    from spstpipe.core.base import BasePlugin as BP2
    from spstpipe.core.registry import discover_plugins as DP2

    assert BP1 is BP2
    assert DP1 is DP2
    assert "BasePlugin" in spstpipe.__all__
    assert "discover_plugins" in spstpipe.__all__
    assert "__version__" in spstpipe.__all__
    assert "__api_version__" in spstpipe.__all__
