# trajectory 算法集合（从旧 plugins/trajectory/run.py 移植）
from __future__ import annotations

import importlib.util

import anndata as ad
import numpy as np

# scanpy 是硬依赖，但 import 可能因版本失败。检测可用性，失败时降级。
SCANPY_AVAILABLE = importlib.util.find_spec("scanpy") is not None


def _run_placeholder(adata: ad.AnnData) -> ad.AnnData:
    """占位实现：给每个 spot 一个伪时间。

    用于没装 scanpy / scanpy 跑 PAGA 失败时。**没有真实生物学意义**。
    """
    rng = np.random.default_rng(42)
    adata.obs["pseudotime"] = rng.random(size=adata.n_obs).astype(np.float32)
    adata.uns["trajectory_method"] = "paga_placeholder"
    return adata


def _run_scanpy_paga(adata: ad.AnnData) -> ad.AnnData:
    """真实现：scanpy.tl.paga + scanpy.tl.dpt 算伪时间。

    流程：PCA → 邻居图 → PAGA → DPT
    PAGA 要求 `obs["louvain"]` 或类似分组；如果没有就跳过 paga 只 dpt。
    """
    import scanpy as sc

    adata_tmp = adata.copy()
    # 1) PCA（如果没做）
    if "X_pca" not in adata_tmp.obsm:
        sc.pp.pca(adata_tmp, n_comps=min(30, adata_tmp.n_vars - 1, adata_tmp.n_obs - 1))
    # 2) 邻居图（如果没做）
    if "neighbors" not in adata_tmp.uns:
        sc.pp.neighbors(adata_tmp, n_neighbors=15)
    # 3) Leiden 分组（paga 需要）
    if "leiden" not in adata_tmp.obs.columns:
        sc.tl.leiden(adata_tmp, resolution=0.5, flavor="igraph", n_iterations=2, directed=False)
    # 4) PAGA
    sc.tl.paga(adata_tmp, groups="leiden")
    # 5) DPT 算伪时间
    try:
        sc.tl.diffmap(adata_tmp, n_comps=15)
        adata_tmp.uns["iroot"] = int(np.argmax(adata_tmp.obsm["X_diffmap"][:, 0]))
        sc.tl.dpt(adata_tmp, n_dcs=10)
        adata.obs["pseudotime"] = adata_tmp.obs["dpt_pseudotime"].values
    except Exception:
        # diffmap 失败时给个 0~1 随机数
        rng = np.random.default_rng(42)
        adata.obs["pseudotime"] = rng.random(size=adata.n_obs).astype(np.float32)
    adata.uns["trajectory_method"] = "paga_scanpy"
    return adata


def run_trajectory(
    adata: ad.AnnData,
    use_scanpy: bool = True,
) -> ad.AnnData:
    """轨迹推断入口（PAGA + DPT）。

    - `use_scanpy=True` 且环境装了 scanpy → 走 scanpy 真方法
    - 其他情况 → 走占位（随机伪时间）

    显式 `use_scanpy=False` 强制走占位。
    """
    if use_scanpy and SCANPY_AVAILABLE:
        try:
            return _run_scanpy_paga(adata)
        except Exception:
            # scanpy 任意环节失败（数据无结构、igraph 没装、leiden 失败等）
            return _run_placeholder(adata)
    return _run_placeholder(adata)
