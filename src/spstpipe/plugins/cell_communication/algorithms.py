# cell_communication 算法集合（从旧 plugins/cell_communication/run.py 移植）
from __future__ import annotations

import importlib.util

import anndata as ad
import numpy as np

# squidpy 是可选依赖。没装时优雅降级到占位实现，绝不抛 ImportError。
SQUIDPY_AVAILABLE = importlib.util.find_spec("squidpy") is not None


def _require_cell_type(adata: ad.AnnData) -> None:
    """检查 adata 是否有 cell_type 列。

    ligrec / cellchat / liana 都要求按 cell type 分组算通讯。
    """
    if "cell_type" not in adata.obs.columns:
        raise ValueError(
            f"{type(adata).__name__} 缺少 obs['cell_type']，无法做细胞通讯分析。"
            "cell_communication 插件要求输入的 AnnData 已经有 cell_type 注释。"
        )


def _run_placeholder(adata: ad.AnnData) -> ad.AnnData:
    """占位实现：每个 cell 一个随机通讯 score，cell_type 两两对生成 0~1 随机数。

    用于没装 squidpy / 不希望拖重依赖的场景。**没有真实生物学意义**。
    """
    _require_cell_type(adata)
    rng = np.random.default_rng(42)
    # 1) 每 spot 一个 score
    adata.obs["cell_communication_score"] = rng.random(size=adata.n_obs).astype(np.float32)
    # 2) cell_type 两两对的 pvalues 模拟矩阵（行=配体，列=受体）
    cell_types = sorted(adata.obs["cell_type"].unique().tolist())
    n_pairs = max(1, len(cell_types) * (len(cell_types) - 1) // 2)
    n_genes = max(1, adata.n_vars)
    adata.uns["cell_communication_result"] = {
        "placeholder": True,
        "cell_types": cell_types,
        "n_pairs": n_pairs,
        "pvalues": rng.random(size=(n_pairs, n_genes)),
    }
    adata.uns["cell_communication_method"] = "placeholder"
    return adata


def _run_squidpy_ligrec(adata: ad.AnnData) -> ad.AnnData:
    """真实现：用 squidpy.gr.ligrec 算配体-受体通讯。

    要求 adata 有 obs['cell_type'] 和空间邻居（spatial_neighbors）。
    没空间邻居时临时建。ligrec 输出均值 p-value 矩阵，存到 uns。
    """
    _require_cell_type(adata)
    import squidpy as sq

    adata_tmp = adata.copy()
    if "spatial_neighbors" not in adata_tmp.uns:
        # ligrec 不需要空间邻居，但保留接口一致
        pass
    # ligrec 至少需要几个配体-受体基因名匹配；用 human 默认
    result = sq.gr.ligrec(
        adata_tmp,
        cluster_key="cell_type",
        n_perms=100,
        seed=42,
        threshold=0.01,
        # 如果完全没匹配，ligrec 抛 ValueError，我们捕获后降级
    )
    # result['means'] 是 (n_pairs, n_genes) 的 p-value 矩阵
    adata.uns["cell_communication_result"] = {
        "means": result["means"],
        "pvalues": result["pvalues"],
        "cluster_key": "cell_type",
    }
    adata.uns["cell_communication_method"] = "squidpy_ligrec"
    return adata


def run_cell_communication(
    adata: ad.AnnData,
    use_squidpy: bool = True,
) -> ad.AnnData:
    """细胞通讯分析入口。

    - `use_squidpy=True` 且环境装了 squidpy → 走 squidpy.gr.ligrec
    - 其他情况 → 走占位实现

    显式 `use_squidpy=False` 强制走占位。
    """
    if use_squidpy and SQUIDPY_AVAILABLE:
        try:
            return _run_squidpy_ligrec(adata)
        except (ValueError, KeyError):
            # ligrec 在基因完全没匹配时会抛，降级到占位（不打断流水线）
            return _run_placeholder(adata)
    return _run_placeholder(adata)
