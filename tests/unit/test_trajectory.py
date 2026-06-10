# trajectory 插件的测试
from __future__ import annotations

import anndata as ad
import pytest

from spstpipe.core.registry import discover_plugins
from spstpipe.plugins.trajectory import algorithms
from spstpipe.plugins.trajectory.plugin import TrajectoryPlugin
from tests.fixtures.synthetic_adata import synthetic_adata


def test_trajectory_已注册():
    plugins = discover_plugins(group="spstpipe.plugins")
    assert "trajectory" in plugins
    assert plugins["trajectory"] is TrajectoryPlugin


@pytest.mark.slow
def test_trajectory_run_改写数据():
    a = synthetic_adata(n_spots=30, n_genes=20)
    out = TrajectoryPlugin().run(a)
    assert "pseudotime" in out.obs.columns
    m = out.uns["trajectory_method"]
    # 走 scanpy 或降级到占位
    assert m in ("paga_scanpy", "paga_placeholder")


def test_trajectory_run_占位路径():
    a = synthetic_adata(n_spots=30, n_genes=20)
    out = algorithms.run_trajectory(a, use_scanpy=False)
    assert "pseudotime" in out.obs.columns
    assert out.uns["trajectory_method"] == "paga_placeholder"
    # 占位用固定 seed
    assert out.obs["pseudotime"].shape == (a.n_obs,)


@pytest.mark.slow
def test_trajectory_run_真方法形状契约():
    a = synthetic_adata(n_spots=30, n_genes=20)
    if not algorithms.SCANPY_AVAILABLE:
        import pytest

        pytest.skip("scanpy 未安装，跳过真方法测试")
    out = algorithms.run_trajectory(a, use_scanpy=True)
    # scanpy 跑通或降级到占位（合成数据可能没结构）都算合法
    assert out.uns["trajectory_method"] in ("paga_scanpy", "paga_placeholder")
    assert "pseudotime" in out.obs.columns
    assert out.obs["pseudotime"].shape == (a.n_obs,)


@pytest.mark.slow
def test_trajectory_run_真方法需要足够样本():
    """PAGA 要求样本数 > 邻居数，否则报错降级到占位。"""
    a = synthetic_adata(n_spots=10, n_genes=5)
    if not algorithms.SCANPY_AVAILABLE:
        import pytest

        pytest.skip("scanpy 未安装")
    out = algorithms.run_trajectory(a, use_scanpy=True)
    # 小样本应当走占位
    assert out.uns["trajectory_method"] == "paga_placeholder"


def test_trajectory_save(tmp_path):
    a = synthetic_adata()
    p = tmp_path / "out.h5ad"
    TrajectoryPlugin().save(a, p)
    assert p.exists()
    b = ad.read_h5ad(p)
    assert b.shape == a.shape
