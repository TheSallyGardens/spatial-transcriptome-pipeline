# spatial_domain 插件的测试
from __future__ import annotations

import anndata as ad
import pytest

from spstpipe.core.registry import discover_plugins
from spstpipe.plugins.spatial_domain import algorithms
from spstpipe.plugins.spatial_domain.plugin import SpatialDomainPlugin
from tests.fixtures.synthetic_adata import synthetic_adata


def test_spatial_domain_已注册():
    plugins = discover_plugins(group="spstpipe.plugins")
    assert "spatial_domain" in plugins
    assert plugins["spatial_domain"] is SpatialDomainPlugin


def test_spatial_domain_默认方法_写_obs_列():
    a = synthetic_adata(n_spots=30, n_genes=20)
    out = SpatialDomainPlugin().run(a)
    assert "spatial_domain" in out.obs.columns
    assert out.uns["spatial_domain_method"] == "spectral_clustering"


def test_spatial_domain_run_谱聚类():
    a = synthetic_adata(n_spots=20, n_genes=20)
    out = algorithms.run_spectral_clustering(a, resolution=0.5)
    assert "spatial_domain" in out.obs.columns
    assert out.uns["spatial_domain_method"] == "spectral_clustering"
    # 至少 2 个 cluster
    assert out.obs["spatial_domain"].nunique() >= 2


def test_spatial_domain_run_需要空间坐标():
    a = synthetic_adata(n_spots=10, n_genes=5)
    del a.obsm["spatial"]
    try:
        algorithms.run_spectral_clustering(a)
    except ValueError as e:
        assert "spatial" in str(e).lower()
    else:
        raise AssertionError("expected ValueError")


@pytest.mark.slow
def test_spatial_domain_run_leiden_真方法形状契约():
    a = synthetic_adata(n_spots=30, n_genes=20)
    if not algorithms.SQUIDPY_AVAILABLE:
        pytest.skip("squidpy 未安装")
    out = algorithms.run_spatial_domain(a, method="leiden", resolution=0.5)
    # leiden 可能成功或降级到谱聚类
    assert out.uns["spatial_domain_method"] in ("leiden_squidpy", "spectral_clustering")
    assert "spatial_domain" in out.obs.columns


def test_spatial_domain_run_占位方法走谱聚类():
    a = synthetic_adata(n_spots=20, n_genes=15)
    out = algorithms.run_spatial_domain(a, method="bayespace", resolution=0.5)
    assert out.uns["spatial_domain_method"] == "spectral_clustering"


def test_spatial_domain_save_写_h5ad(tmp_path):
    a = synthetic_adata()
    p = tmp_path / "out.h5ad"
    SpatialDomainPlugin().save(a, p)
    assert p.exists()
    b = ad.read_h5ad(p)
    assert b.shape == a.shape
