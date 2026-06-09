# multi_sample_integration 插件的测试
from __future__ import annotations

import anndata as ad
import pytest

from spstpipe.core.registry import discover_plugins
from spstpipe.plugins.multi_sample_integration.plugin import MultiSampleIntegrationPlugin
from tests.fixtures.synthetic_adata import synthetic_adata


def test_multi_sample_integration_已注册():
    plugins = discover_plugins(group="spstpipe.plugins")
    assert "multi_sample_integration" in plugins
    assert plugins["multi_sample_integration"] is MultiSampleIntegrationPlugin


def test_multi_sample_integration_run_改_数据():
    a = synthetic_adata(n_spots=30, n_genes=20)
    out = MultiSampleIntegrationPlugin().run(a)
    assert "integration_batch" in out.obs.columns
    assert out.uns["multi_sample_integration_method"] == "harmony"


def test_multi_sample_integration_save(tmp_path):
    a = synthetic_adata()
    p = tmp_path / "out.h5ad"
    MultiSampleIntegrationPlugin().save(a, p)
    assert p.exists()
    b = ad.read_h5ad(p)
    assert b.shape == a.shape
