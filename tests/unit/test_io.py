"""IO 工具的测试。"""

from __future__ import annotations

from spstpipe.core.io import load_anndata, save_anndata
from tests.fixtures.synthetic_adata import synthetic_adata


def test_合成数据_基本形状():
    """synthetic_adata 默认 50 spots x 100 genes。"""
    a = synthetic_adata()
    assert a.shape == (50, 100)
    assert "x" in a.obs.columns
    assert "y" in a.obs.columns
    assert "platform" in a.obs.columns
    assert a.obsm["spatial"].shape == (50, 2)


def test_io_能往返_h5ad(tmp_path):
    """save_anndata / load_anndata 应该保持 shape 和关键 obs/obsm。"""
    a = synthetic_adata(n_spots=20, n_genes=30, platform="stereo_seq")
    p = tmp_path / "test.h5ad"
    save_anndata(a, p)
    b = load_anndata(p)
    assert b.shape == (20, 30)
    assert b.obs["platform"].iloc[0] == "stereo_seq"
    assert b.obsm["spatial"].shape == (20, 2)
    assert b.uns["synthetic"] is True


def test_不同_platform_不影响_io():
    """platform 字段应该被完整保存。"""
    a = synthetic_adata(platform="stereo_seq")
    assert a.obs["platform"].iloc[0] == "stereo_seq"
