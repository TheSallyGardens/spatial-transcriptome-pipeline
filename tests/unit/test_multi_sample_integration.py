# multi_sample_integration 插件的测试
from __future__ import annotations

import anndata as ad
import numpy as np
import pytest

from spstpipe.core.registry import discover_plugins
from spstpipe.plugins.multi_sample_integration import algorithms
from spstpipe.plugins.multi_sample_integration.plugin import MultiSampleIntegrationPlugin
from tests.fixtures.synthetic_adata import synthetic_adata


def _adata_with_batch(n_spots: int = 30, n_genes: int = 20, n_batches: int = 3) -> ad.AnnData:
    a = synthetic_adata(n_spots=n_spots, n_genes=n_genes)
    rng = np.random.default_rng(0)
    a.obs["batch"] = rng.integers(0, n_batches, size=n_spots).astype(str)
    return a


def test_multi_sample_integration_已注册():
    plugins = discover_plugins(group="spstpipe.plugins")
    assert "multi_sample_integration" in plugins
    assert plugins["multi_sample_integration"] is MultiSampleIntegrationPlugin


@pytest.mark.slow
def test_multi_sample_integration_run_改写数据():
    a = _adata_with_batch()
    out = MultiSampleIntegrationPlugin().run(a)
    assert "integration_batch" in out.obs.columns
    m = out.uns["multi_sample_integration_method"]
    assert m in ("harmony_placeholder", "harmony_scanpy")


def test_multi_sample_integration_run_占位路径():
    a = _adata_with_batch()
    out = algorithms.run_integration(a, use_scanpy=False)
    assert "integration_batch" in out.obs.columns
    assert out.uns["multi_sample_integration_method"] == "harmony_placeholder"
    # 占位应当不写 X_pca_harmony
    assert "X_pca_harmony" not in out.obsm


@pytest.mark.slow
def test_multi_sample_integration_run_真方法形状契约():
    a = _adata_with_batch(n_spots=30, n_genes=20)
    if not algorithms.SCANPY_AVAILABLE:
        pytest.skip("scanpy 未安装，跳过真方法测试")
    out = algorithms.run_integration(a, use_scanpy=True)
    # 合成数据可能降级；scanpy 没装则 skip
    assert out.uns["multi_sample_integration_method"] in ("harmony_scanpy", "harmony_placeholder")
    if out.uns["multi_sample_integration_method"] == "harmony_scanpy":
        # 真方法应当写 X_pca_harmony
        assert "X_pca_harmony" in out.obsm
        assert out.obsm["X_pca_harmony"].shape[0] == a.n_obs


def test_multi_sample_integration_run_需要batch():
    a = synthetic_adata()
    try:
        algorithms.run_integration(a, use_scanpy=False)
    except ValueError as e:
        assert "batch" in str(e)
    else:
        raise AssertionError("expected ValueError when obs['batch'] is missing")


def test_multi_sample_integration_save(tmp_path):
    a = _adata_with_batch()
    p = tmp_path / "out.h5ad"
    MultiSampleIntegrationPlugin().save(a, p)
    assert p.exists()
    b = ad.read_h5ad(p)
    assert b.shape == a.shape
