# scrna_joint_analysis 插件的测试
from __future__ import annotations

import anndata as ad
import numpy as np
import pytest

from spstpipe.core.registry import discover_plugins
from spstpipe.plugins.scrna_joint_analysis import algorithms
from spstpipe.plugins.scrna_joint_analysis.plugin import ScRNAJointAnalysisPlugin
from tests.fixtures.synthetic_adata import synthetic_adata


def _make_reference(n_cells: int = 50, n_genes: int = 20, n_types: int = 3) -> ad.AnnData:
    """造 scRNA-seq reference（含 cell_type 列）。"""
    rng = np.random.default_rng(0)
    X = rng.standard_normal((n_cells, n_genes)).astype(np.float32)
    obs = {
        "cell_type": rng.integers(0, n_types, size=n_cells).astype(str),
    }
    return ad.AnnData(X=X, obs=obs, var={"gene_symbol": [f"g{i}" for i in range(n_genes)]})


def test_scrna_joint_analysis_已注册():
    plugins = discover_plugins(group="spstpipe.plugins")
    assert "scrna_joint_analysis" in plugins
    assert plugins["scrna_joint_analysis"] is ScRNAJointAnalysisPlugin


@pytest.mark.slow
def test_scrna_joint_analysis_run_改写数据():
    a = synthetic_adata(n_spots=30, n_genes=20)
    out = ScRNAJointAnalysisPlugin().run(a)
    assert "predicted_cell_type" in out.obs.columns
    m = out.uns["scrna_joint_analysis_method"]
    assert m in ("seurat_placeholder", "seurat_scanpy_ingest")


def test_scrna_joint_analysis_run_占位路径():
    a = synthetic_adata(n_spots=30, n_genes=20)
    out = algorithms.run_joint_analysis(a, reference=None, use_scanpy=False)
    assert "predicted_cell_type" in out.obs.columns
    assert out.uns["scrna_joint_analysis_method"] == "seurat_placeholder"


@pytest.mark.slow
def test_scrna_joint_analysis_run_真方法形状契约():
    a = synthetic_adata(n_spots=20, n_genes=20)
    ref = _make_reference(n_cells=30, n_genes=20, n_types=3)
    if not algorithms.SCANPY_AVAILABLE:
        pytest.skip("scanpy 未安装，跳过真方法测试")
    out = algorithms.run_joint_analysis(a, reference=ref, use_scanpy=True)
    assert out.uns["scrna_joint_analysis_method"] in ("seurat_scanpy_ingest", "seurat_placeholder")
    if out.uns["scrna_joint_analysis_method"] == "seurat_scanpy_ingest":
        assert "predicted_cell_type" in out.obs.columns
        assert out.obs["predicted_cell_type"].shape == (a.n_obs,)


def test_scrna_joint_analysis_save(tmp_path):
    a = synthetic_adata()
    p = tmp_path / "out.h5ad"
    ScRNAJointAnalysisPlugin().save(a, p)
    assert p.exists()
    b = ad.read_h5ad(p)
    assert b.shape == a.shape
