# spatial_variable_genes 插件的测试
from __future__ import annotations

import anndata as ad

from spstpipe.core.registry import discover_plugins
from spstpipe.plugins.spatial_variable_genes import algorithms
from spstpipe.plugins.spatial_variable_genes.plugin import SpatialVariableGenesPlugin
from tests.fixtures.synthetic_adata import synthetic_adata


def test_spatial_variable_genes_已注册():
    plugins = discover_plugins(group="spstpipe.plugins")
    assert "spatial_variable_genes" in plugins
    assert plugins["spatial_variable_genes"] is SpatialVariableGenesPlugin


def test_spatial_variable_genes_run_改写数据():
    a = synthetic_adata(n_spots=30, n_genes=20)
    out = SpatialVariableGenesPlugin().run(a)
    assert "spatial_variable" in out.var.columns
    # method 字段记录实际走的实现（占位或 squidpy），两种都是合法""morans_i"" 族
    m = out.uns["spatial_variable_genes_method"]
    assert m in ("morans_i_placeholder", "morans_i_squidpy")


def test_spatial_variable_genes_run_占位路径():
    """没装 squidpy 时应当走占位实现，不抛错。"""
    a = synthetic_adata(n_spots=30, n_genes=20)
    # 强制走占位
    out = algorithms.run_morans_i(a, use_squidpy=False)
    assert "spatial_variable" in out.var.columns
    assert out.var["spatial_variable"].shape == (a.n_vars,)
    # 占位用固定 seed，值应该等于 rng(42).random(n_vars) 之类
    assert out.uns["spatial_variable_genes_method"] == "morans_i_placeholder"


def test_spatial_variable_genes_run_真方法形状契约():
    """真方法（squidpy）应输出 spatial_variable 和 spatial_variable_pval 两列。"""
    a = synthetic_adata(n_spots=30, n_genes=20)
    if not algorithms.SQUIDPY_AVAILABLE:
        # 没装 squidpy，跳过；不算测试失败
        import pytest

        pytest.skip("squidpy 未安装，跳过真方法测试")
    out = algorithms.run_morans_i(a, use_squidpy=True)
    assert "spatial_variable" in out.var.columns
    assert "spatial_variable_pval" in out.var.columns
    assert out.var["spatial_variable"].shape == (a.n_vars,)
    assert out.var["spatial_variable_pval"].shape == (a.n_vars,)
    assert out.uns["spatial_variable_genes_method"] == "morans_i_squidpy"


def test_spatial_variable_genes_run_需要空间坐标():
    """没空间坐标时应当抛 ValueError（占位 + 真方法一致）。"""
    a = synthetic_adata(n_spots=10, n_genes=5)
    del a.obsm["spatial"]  # 去掉空间坐标
    try:
        algorithms.run_morans_i(a, use_squidpy=False)
    except ValueError as e:
        assert "spatial" in str(e).lower()
    else:
        raise AssertionError("expected ValueError when spatial obsm is missing")


def test_spatial_variable_genes_save(tmp_path):
    a = synthetic_adata()
    p = tmp_path / "out.h5ad"
    SpatialVariableGenesPlugin().save(a, p)
    assert p.exists()
    b = ad.read_h5ad(p)
    assert b.shape == a.shape
