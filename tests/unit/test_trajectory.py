# trajectory 插件的测试
from __future__ import annotations

import anndata as ad

from spstpipe.core.registry import discover_plugins
from spstpipe.plugins.trajectory.plugin import TrajectoryPlugin
from tests.fixtures.synthetic_adata import synthetic_adata


def test_trajectory_已注册():
    plugins = discover_plugins(group="spstpipe.plugins")
    assert "trajectory" in plugins
    assert plugins["trajectory"] is TrajectoryPlugin


def test_trajectory_run_改_数据():
    a = synthetic_adata(n_spots=30, n_genes=20)
    out = TrajectoryPlugin().run(a)
    assert "pseudotime" in out.obs.columns
    assert out.uns["trajectory_method"] == "paga"


def test_trajectory_save(tmp_path):
    a = synthetic_adata()
    p = tmp_path / "out.h5ad"
    TrajectoryPlugin().save(a, p)
    assert p.exists()
    b = ad.read_h5ad(p)
    assert b.shape == a.shape
