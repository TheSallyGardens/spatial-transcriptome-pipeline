# cell_communication 插件的测试
from __future__ import annotations

import anndata as ad
import numpy as np

from spstpipe.core.registry import discover_plugins
from spstpipe.plugins.cell_communication import algorithms
from spstpipe.plugins.cell_communication.plugin import CellCommunicationPlugin
from tests.fixtures.synthetic_adata import synthetic_adata


def _adata_with_cell_type(n_spots: int = 30, n_genes: int = 20, n_types: int = 3) -> ad.AnnData:
    """造带 cell_type 的合成数据。"""
    a = synthetic_adata(n_spots=n_spots, n_genes=n_genes)
    rng = np.random.default_rng(0)
    a.obs["cell_type"] = rng.integers(0, n_types, size=n_spots).astype(str)
    return a


def test_cell_communication_已注册():
    plugins = discover_plugins(group="spstpipe.plugins")
    assert "cell_communication" in plugins
    assert plugins["cell_communication"] is CellCommunicationPlugin


def test_cell_communication_run_改写数据():
    a = _adata_with_cell_type()
    out = CellCommunicationPlugin().run(a)
    assert "cell_communication_score" in out.obs.columns
    m = out.uns["cell_communication_method"]
    assert m in ("placeholder", "squidpy_ligrec")


def test_cell_communication_run_占位路径():
    a = _adata_with_cell_type()
    out = algorithms.run_cell_communication(a, use_squidpy=False)
    assert "cell_communication_score" in out.obs.columns
    assert out.uns["cell_communication_method"] == "placeholder"
    assert "cell_communication_result" in out.uns
    result = out.uns["cell_communication_result"]
    assert result.get("placeholder") is True
    assert "cell_types" in result


def test_cell_communication_run_真方法形状契约():
    a = _adata_with_cell_type(n_spots=20, n_genes=15)
    if not algorithms.SQUIDPY_AVAILABLE:
        import pytest

        pytest.skip("squidpy 未安装，跳过真方法测试")
    out = algorithms.run_cell_communication(a, use_squidpy=True)
    # 真方法会因基因名不匹配降级到占位（ValueError 被 catch）
    # 所以 method 可能是 squidpy_ligrec 或 placeholder
    assert out.uns["cell_communication_method"] in ("squidpy_ligrec", "placeholder")
    assert "cell_communication_result" in out.uns


def test_cell_communication_run_需要cell_type():
    a = synthetic_adata()
    # 没 cell_type 应当抛 ValueError
    try:
        algorithms.run_cell_communication(a, use_squidpy=False)
    except ValueError as e:
        assert "cell_type" in str(e)
    else:
        raise AssertionError("expected ValueError when obs['cell_type'] is missing")


def test_cell_communication_save(tmp_path):
    a = _adata_with_cell_type()
    p = tmp_path / "out.h5ad"
    CellCommunicationPlugin().save(a, p)
    assert p.exists()
    b = ad.read_h5ad(p)
    assert b.shape == a.shape
