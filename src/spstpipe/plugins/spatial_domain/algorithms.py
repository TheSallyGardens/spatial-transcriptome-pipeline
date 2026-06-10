# spatial_domain 算法集合（从旧 plugins/spatial_domain/run.py 移植）
from __future__ import annotations

import importlib.util

import anndata as ad
import numpy as np

# squidpy + igraph 是可选依赖
SQUIDPY_AVAILABLE = importlib.util.find_spec("squidpy") is not None


def _require_spatial(adata: ad.AnnData) -> None:
    """检查 adata 是否有空间坐标。"""
    if "spatial" not in adata.obsm:
        raise ValueError(
            f"{type(adata).__name__} 缺少 obsm['spatial']，无法做空间域识别。"
            "spatial_domain 插件要求输入的 AnnData 已经预处理好空间坐标。"
        )


def calculate_adj_matrix(
    x: np.ndarray,
    y: np.ndarray,
    x_bins: np.ndarray | None = None,
    y_bins: np.ndarray | None = None,
    image: np.ndarray | None = None,
    beta: float = 0.5,
    alpha: float = 0.1,
) -> np.ndarray:
    """计算空间邻接矩阵（高斯核 + 可选图像权重）。"""
    n = len(x)
    dist_mat = np.zeros((n, n))
    for i in range(n):
        dist_mat[i, :] = np.sqrt((x[i] - x) ** 2 + (y[i] - y) ** 2)
    sigma = np.median(dist_mat[dist_mat > 0]) if (dist_mat > 0).any() else 1.0
    weight_matrix = np.exp(-(dist_mat**2) / (2 * sigma**2))
    np.fill_diagonal(weight_matrix, 0)
    if image is not None and x_bins is not None and y_bins is not None:
        image_weight = np.exp(-alpha * image)
        weight_matrix = beta * weight_matrix + (1 - beta) * image_weight
    return weight_matrix


def run_spectral_clustering(adata: ad.AnnData, resolution: float = 0.5) -> ad.AnnData:
    """基于空间坐标的谱聚类（无重依赖，纯 numpy + sklearn）。"""
    from scipy.spatial import distance
    from sklearn.cluster import SpectralClustering

    _require_spatial(adata)
    coords = adata.obsm["spatial"]
    dist_mat = distance.squareform(distance.pdist(coords))
    adj = np.exp(-(dist_mat**2) / (2 * 100**2))
    np.fill_diagonal(adj, 0)

    n_clusters = int(resolution * 10) if resolution < 1 else max(2, int(resolution))
    n_clusters = max(2, min(n_clusters, adata.n_obs - 1, 20))
    clustering = SpectralClustering(
        n_clusters=n_clusters, affinity="precomputed", random_state=42, assign_labels="kmeans"
    ).fit_predict(adj)
    adata.obs["spatial_domain"] = clustering.astype(str)
    adata.uns["spatial_domain_method"] = "spectral_clustering"
    return adata


def run_leiden(adata: ad.AnnData, resolution: float = 0.5) -> ad.AnnData:
    """基于 squidpy.gr.spatial_neighbors + scanpy.tl.leiden 的空间聚类。

    流程：spatial_neighbors → leiden → 写 obs['spatial_domain']
    要求 squidpy + scanpy + igraph（leiden algorithm）。
    """
    import scanpy as sc
    import squidpy as sq

    _require_spatial(adata)
    adata_tmp = adata.copy()
    sq.gr.spatial_neighbors(adata_tmp, coord_type="generic")
    sc.tl.leiden(adata_tmp, resolution=resolution, flavor="igraph", n_iterations=2, directed=False)
    adata.obs["spatial_domain"] = adata_tmp.obs["leiden"].astype(str).values
    adata.uns["spatial_domain_method"] = "leiden_squidpy"
    adata.uns["spatial_domain_n_domains"] = int(adata_tmp.obs["leiden"].nunique())
    return adata


def run_spatial_domain(
    adata: ad.AnnData,
    method: str = "spectral_clustering",
    resolution: float = 0.5,
) -> ad.AnnData:
    """空间域识别统一入口。

    - method='spectral_clustering' → 谱聚类（无重依赖）
    - method='leiden' → squidpy+leiden（需要装 squidpy）
    - method='placeholder' / 'spagcn' / 'bayespace' / 'stlearn' → 走 spectral_clustering 兜底
    """
    if method == "leiden" and SQUIDPY_AVAILABLE:
        try:
            return run_leiden(adata, resolution=resolution)
        except Exception:
            # leiden 失败（igraph 没装、邻居数不够）降级到谱聚类
            return run_spectral_clustering(adata, resolution=resolution)
    return run_spectral_clustering(adata, resolution=resolution)
