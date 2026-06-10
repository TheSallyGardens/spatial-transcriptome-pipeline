# scrna_joint_analysis 插件的测试
from __future__ import annotations

import anndata as ad

from spstpipe.core.registry import discover_plugins
from spstpipe.plugins.scrna_joint_analysis.plugin import ScRNAJointAnalysisPlugin
from tests.fixtures.synthetic_adata import synthetic_adata


def test_scrna_joint_analysis_已注册():
    plugins = discover_plugins(group="spstpipe.plugins")
    assert "scrna_joint_analysis" in plugins
    assert plugins["scrna_joint_analysis"] is ScRNAJointAnalysisPlugin


def test_scrna_joint_analysis_run_改_数据():
    a = synthetic_adata(n_spots=30, n_genes=20)
    out = ScRNAJointAnalysisPlugin().run(a)
    assert "predicted_cell_type" in out.obs.columns
    assert out.uns["scrna_joint_analysis_method"] == "seurat"


def test_scrna_joint_analysis_save(tmp_path):
    a = synthetic_adata()
    p = tmp_path / "out.h5ad"
    ScRNAJointAnalysisPlugin().save(a, p)
    assert p.exists()
    b = ad.read_h5ad(p)
    assert b.shape == a.shape
