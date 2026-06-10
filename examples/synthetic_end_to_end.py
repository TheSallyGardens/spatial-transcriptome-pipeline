"""spstpipe 端到端 demo：合成 AnnData → 6 个内置插件 → out.h5ad。

用法：python examples/synthetic_end_to_end.py

不需要任何真实数据，**完全离线**。用于快速验证你的安装。
"""
from __future__ import annotations

from pathlib import Path

import anndata as ad
import numpy as np

from spstpipe.plugins.cell_communication.plugin import CellCommunicationPlugin
from spstpipe.plugins.multi_sample_integration.plugin import MultiSampleIntegrationPlugin
from spstpipe.plugins.scrna_joint_analysis.plugin import ScRNAJointAnalysisPlugin
from spstpipe.plugins.spatial_domain.plugin import SpatialDomainPlugin
from spstpipe.plugins.spatial_variable_genes.plugin import SpatialVariableGenesPlugin
from spstpipe.plugins.trajectory.plugin import TrajectoryPlugin
from tests.fixtures.synthetic_adata import synthetic_adata


def step(msg: str) -> None:
    print(f"==> {msg}")


def ok(msg: str) -> None:
    print(f"    [OK] {msg}")


def main() -> None:
    out_path = Path("out.h5ad")

    # 1) 造合成数据
    step("造合成数据 (50 spots x 100 genes, 5x10 网格)")
    adata = synthetic_adata(n_spots=50, n_genes=100, platform="10x_visium_synthetic", seed=0)
    ok(f"{adata.n_obs} spots x {adata.n_vars} genes")

    # 2) spatial_domain（谱聚类，无依赖）
    step("跑 spatial_domain (spectral_clustering)")
    adata = SpatialDomainPlugin().run(adata)  # 谱聚类（无依赖）
    n_domains = adata.obs["spatial_domain"].nunique()
    ok(f"{n_domains} domains")

    # 3) spatial_variable_genes（占位 Moran's I）
    step("跑 spatial_variable_genes (morans_i_placeholder)")
    adata = SpatialVariableGenesPlugin(use_squidpy=False).run(adata)
    n_genes_scored = adata.var["spatial_variable"].notna().sum()
    ok(f"{n_genes_scored} gene scores")

    # 4) cell_communication（占位，注入 cell_type）
    step("跑 cell_communication (placeholder)")
    rng = np.random.default_rng(42)
    adata.obs["cell_type"] = rng.integers(0, 3, size=adata.n_obs).astype(str)
    adata = CellCommunicationPlugin(use_squidpy=False).run(adata)
    n_scored = adata.obs["cell_communication_score"].notna().sum()
    ok(f"{n_scored} cell communication scores")

    # 5) trajectory（占位 PAGA）
    step("跑 trajectory (paga_placeholder)")
    adata = TrajectoryPlugin(use_scanpy=False).run(adata)
    n_pseudo = adata.obs["pseudotime"].notna().sum()
    ok(f"{n_pseudo} pseudotime")

    # 6) multi_sample_integration（占位，注入 batch）
    step("跑 multi_sample_integration (harmony_placeholder)")
    adata.obs["batch"] = rng.integers(0, 2, size=adata.n_obs).astype(str)
    adata = MultiSampleIntegrationPlugin(use_scanpy=False).run(adata)
    n_batches = adata.obs["integration_batch"].nunique()
    ok(f"{n_batches} batches")

    # 7) scrna_joint_analysis（占位）
    step("跑 scrna_joint_analysis (seurat_placeholder)")
    adata = ScRNAJointAnalysisPlugin(use_scanpy=False).run(adata)
    n_pred = adata.obs["predicted_cell_type"].nunique()
    ok(f"{n_pred} predicted cell types")

    # 8) 保存
    step(f"保存 {out_path}")
    adata.write_h5ad(out_path)
    ok(f"{out_path} ({adata.n_obs} x {adata.n_vars})")


if __name__ == "__main__":
    main()
