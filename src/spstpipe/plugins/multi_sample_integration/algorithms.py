# multi_sample_integration 算法集合（从旧 plugins/multi_sample_integration/run.py 移植）
from __future__ import annotations

import importlib.util

import anndata as ad

# scanpy 是硬依赖，但 import 可能因版本失败。检测可用性，失败时降级。
SCANPY_AVAILABLE = importlib.util.find_spec("scanpy") is not None


def _require_batch(adata: ad.AnnData) -> None:
    """检查 adata 是否有 batch 列。Harmony / BBKNN / LIGER 都按 batch 校正。"""
    if "batch" not in adata.obs.columns:
        raise ValueError(
            f"{type(adata).__name__} 缺少 obs['batch']，无法做多样本整合。"
            "multi_sample_integration 插件要求输入的 AnnData 已经有 batch 标签。"
        )


def _run_placeholder(adata: ad.AnnData) -> ad.AnnData:
    """占位实现：把 batch 列复制到 integration_batch（标记已经"整合"了）。

    用于没装 scanpy / scanpy 跑 harmony 失败时。**没有真实整合效果**。
    """
    _require_batch(adata)
    adata.obs["integration_batch"] = adata.obs["batch"].astype(str)
    adata.uns["multi_sample_integration_method"] = "harmony_placeholder"
    return adata


def _run_scanpy_harmony(adata: ad.AnnData) -> ad.AnnData:
    """真实现：scanpy.external.pp.harmony_align 整合多样本。

    流程：PCA（如果没做）→ harmony_align → 输出校正后 PCA 到 obsm["X_pca_harmony"]。
    """
    import scanpy as sc
    import scanpy.external as sce

    _require_batch(adata)
    adata_tmp = adata.copy()
    # 1) PCA
    if "X_pca" not in adata_tmp.obsm:
        n_comp = min(30, adata_tmp.n_vars - 1, adata_tmp.n_obs - 1)
        sc.pp.pca(adata_tmp, n_comps=n_comp)
    # 2) Harmony
    sce.pp.harmony_integrate(adata_tmp, key="batch", max_iter_harmony=20)
    # 写回原 adata
    adata.obsm["X_pca_harmony"] = adata_tmp.obsm["X_pca_harmony"]
    adata.obs["integration_batch"] = adata.obs["batch"].astype(str)
    adata.uns["multi_sample_integration_method"] = "harmony_scanpy"
    return adata


def run_integration(
    adata: ad.AnnData,
    use_scanpy: bool = True,
) -> ad.AnnData:
    """多样本整合入口（Harmony）。

    - `use_scanpy=True` 且环境装了 scanpy → 走 scanpy 真方法
    - 其他情况 → 走占位

    显式 `use_scanpy=False` 强制走占位。
    """
    if use_scanpy and SCANPY_AVAILABLE:
        try:
            return _run_scanpy_harmony(adata)
        except Exception:
            return _run_placeholder(adata)
    return _run_placeholder(adata)
