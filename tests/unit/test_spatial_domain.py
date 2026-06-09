"""spatial_domain 插件的测试。"""
from __future__ import annotations

import anndata as ad
import numpy as np
import pytest

from spstpipe.core.registry import discover_plugins
from spstpipe.plugins.spatial_domain.plugin import SpatialDomainPlugin
from tests.fixtures.synthetic_adata import synthetic_adata


def test_spatial_domain_已注册():
    """spstpipe.plugins 组里应该能找到 spatial_domain。"""
    plugins = discover_plugins(group="spstpipe.plugins")
    assert "spatial_domain" in plugins
    assert plugins["spatial_domain"] is SpatialDomainPlugin


def test_spatial_domain_默认_方法_加_obs_列():
    """默认方法（spectral clustering）应该在 obs 里加 spatial_domain 列。"""
    a = synthetic_adata(n_spots=50, n_genes=20)
    out = SpatialDomainPlugin().run(a)
    assert "spatial_domain" in out.obs.columns
    # 至少要有 2 个不同域
    assert out.obs["spatial_domain"].nunique() >= 2


def test_spatial_domain_preprocess_保持_AnnData():
    """preprocess 应该返回 AnnData，不修改 obs 关键列。"""
    a = synthetic_adata()
    out = SpatialDomainPlugin().preprocess(a)
    assert isinstance(out, ad.AnnData)
    assert out.shape == a.shape
    assert "x" in out.obs.columns


def test_spatial_domain_save_写_h5ad(tmp_path):
    """save 应该写出 h5ad 文件。"""
    a = synthetic_adata()
    p = tmp_path / "out.h5ad"
    SpatialDomainPlugin().save(a, p)
    assert p.exists()
    assert p.stat().st_size > 0
    # 读回来验证
    b = ad.read_h5ad(p)
    assert b.shape == a.shape


@pytest.mark.parametrize("method", ["spectral_clustering", "placeholder"])
def test_spatial_domain_指定方法(method):
    """明确指定方法名时，应该用对应算法（placeholder 就是谱聚类兜底）。"""
    a = synthetic_adata(n_spots=40, n_genes=20)
    out = SpatialDomainPlugin(method=method).run(a)
    assert "spatial_domain" in out.obs.columns