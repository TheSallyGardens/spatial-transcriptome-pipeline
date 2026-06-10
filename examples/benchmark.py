"""spstpipe 性能基准：4 个规模跑 6 plugin 全流程。

用法：python examples/benchmark.py
"""
from __future__ import annotations

import time
from pathlib import Path

import anndata as ad
import numpy as np

from spstpipe.plugins.cell_communication.plugin import CellCommunicationPlugin
from spstpipe.plugins.multi_sample_integration.plugin import MultiSampleIntegrationPlugin
from spstpipe.plugins.scrna_joint_analysis.plugin import ScRNAJointAnalysisPlugin
from spstpipe.plugins.spatial_domain.plugin import SpatialDomainPlugin
from spstpipe.plugins.spatial_variable_genes.plugin import SpatialVariableGenesPlugin
from spstpipe.plugins.trajectory.plugin import TrajectoryPlugin


SIZES = [
    (50, 100, "小"),
    (500, 1000, "中"),
    (5000, 5000, "大"),
    (20000, 5000, "极大"),
]


def make_adata(n_spots: int, n_genes: int, seed: int = 0) -> ad.AnnData:
    """造合成 AnnData：n_spots × n_genes 高斯噪声 + sqrt 网格坐标。"""
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n_spots, n_genes)).astype(np.float32)
    side = int(np.ceil(np.sqrt(n_spots)))
    x = np.tile(np.arange(side, dtype=float), side)[:n_spots]
    y = np.repeat(np.arange(side, dtype=float), side)[:n_spots]
    adata = ad.AnnData(
        X=X,
        obs={"x": x, "y": y, "platform": "10x_visium_synthetic"},
        var={"gene_symbol": [f"g{i}" for i in range(n_genes)]},
        obsm={"spatial": np.column_stack([x, y])},
    )
    return adata


def run_pipeline(adata: ad.AnnData) -> None:
    """跑 6 plugin 全流程（占位优先，最快）。"""
    rng = np.random.default_rng(0)
    adata.obs["cell_type"] = rng.integers(0, 3, size=adata.n_obs).astype(str)
    adata.obs["batch"] = rng.integers(0, 2, size=adata.n_obs).astype(str)

    adata = SpatialDomainPlugin().run(adata)
    adata = SpatialVariableGenesPlugin(use_squidpy=False).run(adata)
    adata = CellCommunicationPlugin(use_squidpy=False).run(adata)
    adata = TrajectoryPlugin(use_scanpy=False).run(adata)
    adata = MultiSampleIntegrationPlugin(use_scanpy=False).run(adata)
    adata = ScRNAJointAnalysisPlugin(use_scanpy=False).run(adata)


def main() -> None:
    print("spstpipe 性能基准（6 plugin 全流程，占位方法）")
    print(f"  Python {Path(__file__).name} 跑 {len(SIZES)} 个规模")
    print()
    for n_spots, n_genes, label in SIZES:
        adata = make_adata(n_spots, n_genes)
        t0 = time.perf_counter()
        run_pipeline(adata)
        elapsed = time.perf_counter() - t0
        print(f"  [{label:>4}] {n_spots:>6} spots x {n_genes:>5} genes | 耗时 {elapsed:6.2f} 秒")


if __name__ == "__main__":
    main()
