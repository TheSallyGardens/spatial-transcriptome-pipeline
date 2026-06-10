# spatial_variable_genes 插件的测试
from __future__ import annotations

import anndata as ad

from spstpipe.core.registry import discover_plugins
from spstpipe.plugins.spatial_variable_genes.plugin import SpatialVariableGenesPlugin
from tests.fixtures.synthetic_adata import synthetic_adata


def test_spatial_variable_genes_已注册():
    plugins = discover_plugins(group="spstpipe.plugins")
    assert "spatial_variable_genes" in plugins
    assert plugins["spatial_variable_genes"] is SpatialVariableGenesPlugin


def test_spatial_variable_genes_run_改_数据():
    a = synthetic_adata(n_spots=30, n_genes=20)
    out = SpatialVariableGenesPlugin().run(a)
    assert "spatial_variable" in out.var.columns
    assert out.uns["spatial_variable_genes_method"] == "morans_i"


def test_spatial_variable_genes_save(tmp_path):
    a = synthetic_adata()
    p = tmp_path / "out.h5ad"
    SpatialVariableGenesPlugin().save(a, p)
    assert p.exists()
    b = ad.read_h5ad(p)
    assert b.shape == a.shape
