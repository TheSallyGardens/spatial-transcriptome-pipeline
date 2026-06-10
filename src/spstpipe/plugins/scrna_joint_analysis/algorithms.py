# scrna_joint_analysis 算法集合（从旧 plugins/scrna_joint_analysis/run.py 移植）
from __future__ import annotations

import importlib.util

import anndata as ad
import numpy as np

# scanpy 是硬依赖
SCANPY_AVAILABLE = importlib.util.find_spec("scanpy") is not None


def _run_placeholder(adata: ad.AnnData) -> ad.AnnData:
    """占位实现：每个 spot 一个随机 cell_type。

    用于没装 scanpy / 没 reference 时。**没有真实 label transfer**。
    """
    rng = np.random.default_rng(42)
    adata.obs["predicted_cell_type"] = rng.integers(0, 3, size=adata.n_obs).astype(str)
    adata.uns["scrna_joint_analysis_method"] = "seurat_placeholder"
    return adata


def _run_scanpy_ingest(adata: ad.AnnData, reference: ad.AnnData) -> ad.AnnData:
    """真实现：scanpy.tl.ingest 把 reference 的 cell_type label 投影到 adata。

    要求 reference 有 obs['cell_type'] 且两者共享高变基因。失败时降级到占位。
    """
    import scanpy as sc

    if "cell_type" not in reference.obs.columns:
        raise ValueError("reference.obs 必须有 'cell_type' 列")

    adata_tmp = adata.copy()
    ref_tmp = reference.copy()
    # 共享高变基因（取交集）
    common_genes = adata_tmp.var_names.intersection(ref_tmp.var_names)
    if len(common_genes) < 10:
        raise ValueError(
            f"adata 和 reference 共享高变基因太少（{len(common_genes)} < 10），ingest 效果不可靠。"
        )
    adata_tmp = adata_tmp[:, common_genes].copy()
    ref_tmp = ref_tmp[:, common_genes].copy()
    # 标准预处理
    sc.pp.normalize_total(ref_tmp, target_sum=1e4)
    sc.pp.log1p(ref_tmp)
    sc.pp.normalize_total(adata_tmp, target_sum=1e4)
    sc.pp.log1p(adata_tmp)
    # 在 reference 上做 PCA + neighbors + umap（必须先有这些）
    if "X_pca" not in ref_tmp.obsm:
        sc.pp.pca(ref_tmp, n_comps=min(30, ref_tmp.n_vars - 1, ref_tmp.n_obs - 1))
    if "neighbors" not in ref_tmp.uns:
        sc.pp.neighbors(ref_tmp, n_neighbors=15)
    if "X_umap" not in ref_tmp.obsm:
        sc.tl.umap(ref_tmp)
    # ingest
    sc.tl.ingest(adata_tmp, ref_tmp, obs="cell_type")
    # 写回
    adata.obs["predicted_cell_type"] = adata_tmp.obs["cell_type"].astype(str).values
    adata.uns["scrna_joint_analysis_method"] = "seurat_scanpy_ingest"
    adata.uns["scrna_joint_reference_n_cells"] = int(ref_tmp.n_obs)
    adata.uns["scrna_joint_reference_n_types"] = int(ref_tmp.obs["cell_type"].nunique())
    return adata


def run_joint_analysis(
    adata: ad.AnnData,
    reference: ad.AnnData | None = None,
    use_scanpy: bool = True,
) -> ad.AnnData:
    """scRNA + spatial 联合分析入口（label transfer）。

    - `reference` 给定且 use_scanpy=True → scanpy.tl.ingest 真方法
    - 其他情况 → 走占位（随机 cell_type）

    显式 `use_scanpy=False` 强制占位。
    """
    if use_scanpy and SCANPY_AVAILABLE and reference is not None:
        try:
            return _run_scanpy_ingest(adata, reference)
        except Exception:
            return _run_placeholder(adata)
    return _run_placeholder(adata)
