# cell_communication 插件的测试
from __future__ import annotations

import anndata as ad

from spstpipe.core.registry import discover_plugins
from spstpipe.plugins.cell_communication.plugin import CellCommunicationPlugin
from tests.fixtures.synthetic_adata import synthetic_adata


def test_cell_communication_已注册():
    plugins = discover_plugins(group="spstpipe.plugins")
    assert "cell_communication" in plugins
    assert plugins["cell_communication"] is CellCommunicationPlugin


def test_cell_communication_run_改_数据():
    a = synthetic_adata(n_spots=30, n_genes=20)
    out = CellCommunicationPlugin().run(a)
    assert "cell_communication_score" in out.obs.columns
    assert out.uns["cell_communication_method"] == "placeholder"


def test_cell_communication_save(tmp_path):
    a = synthetic_adata()
    p = tmp_path / "out.h5ad"
    CellCommunicationPlugin().save(a, p)
    assert p.exists()
    b = ad.read_h5ad(p)
    assert b.shape == a.shape
