# spatial_variable_genes 算法集合（从旧 plugins/spatial_variable_genes/run.py 移植）
from __future__ import annotations

import importlib.util

import anndata as ad
import numpy as np

# squidpy 是可选依赖。没装时优雅降级到占位实现，绝不抛 ImportError。
SQUIDPY_AVAILABLE = importlib.util.find_spec("squidpy") is not None


def _require_spatial(adata: ad.AnnData) -> None:
    """检查 adata 是否有空间坐标，没有就抛 ValueError（不抛 ImportError）。"""
    if "spatial" not in adata.obsm:
        raise ValueError(
            f"{type(adata).__name__} 缺少 obsm['spatial']，无法做空间统计。"
            "spatial_variable_genes 插件要求输入的 AnnData 已经预处理好空间坐标。"
        )


def _run_placeholder(adata: ad.AnnData) -> ad.AnnData:
    """占位实现：给每个基因一个随机 score。

    用于没装 squidpy / 不希望拖重依赖的场景。结构稳定，但**没有真实空间信号**。
    """
    _require_spatial(adata)
    rng = np.random.default_rng(42)
    adata.var["spatial_variable"] = rng.random(size=adata.n_vars)
    adata.uns["spatial_variable_genes_method"] = "morans_i_placeholder"
    return adata


def _run_squidpy(adata: ad.AnnData) -> ad.AnnData:
    """真实现：用 squidpy.gr.spatial_autocorr 算 Moran's I + p-value。

    要求输入已经 `sq.gr.spatial_neighbors(adata)` 过；如果没做，临时算一下。
    """
    _require_spatial(adata)
    import squidpy as sq

    # 临时建邻居图（不写回 adata），避免污染调用方
    adata_tmp = adata.copy()
    if "spatial_neighbors" not in adata_tmp.uns:
        sq.gr.spatial_neighbors(adata_tmp, coord_type="generic")
    # spatial_autocorr 默认 mode='moran'，输出 I 和 pval
    result = sq.gr.spatial_autocorr(adata_tmp, mode="moran", n_perms=100, seed=42)
    # result 是 DataFrame，index 是 var_names，列是 'I' 和 'pval_norm'
    adata.var["spatial_variable"] = result["I"].reindex(adata.var_names).values
    adata.var["spatial_variable_pval"] = result["pval_norm"].reindex(adata.var_names).values
    adata.uns["spatial_variable_genes_method"] = "morans_i_squidpy"
    return adata


def run_morans_i(
    adata: ad.AnnData,
    use_squidpy: bool = True,
) -> ad.AnnData:
    """Moran's I 空间自相关分析入口。

    - `use_squidpy=True` 且环境装了 squidpy → 走 squidpy.gr.spatial_autocorr
    - 其他情况 → 走占位实现（随机 score，仅用于演示流程）

    显式 `use_squidpy=False` 强制走占位，方便测试和无依赖场景。
    """
    if use_squidpy and SQUIDPY_AVAILABLE:
        return _run_squidpy(adata)
    return _run_placeholder(adata)
