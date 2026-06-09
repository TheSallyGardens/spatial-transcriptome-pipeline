# spatial_domain 算法集合（从老 plugins/spatial_domain/run.py 移植）
from __future__ import annotations

import numpy as np
import anndata as ad


def calculate_adj_matrix(x, y, x_bins=None, y_bins=None, image=None, beta=0.5, alpha=0.1):
    """计算空间邻接矩阵（高斯核 + 可选图像权重）。"""
    n = len(x)
    dist_mat = np.zeros((n, n))
    for i in range(n):
        dist_mat[i, :] = np.sqrt((x[i] - x) ** 2 + (y[i] - y) ** 2)
    sigma = np.median(dist_mat[dist_mat > 0]) if (dist_mat > 0).any() else 1.0
    weight_matrix = np.exp(-dist_mat ** 2 / (2 * sigma ** 2))
    np.fill_diagonal(weight_matrix, 0)
    if image is not None and x_bins is not None and y_bins is not None:
        image_weight = np.exp(-alpha * image)
        weight_matrix = beta * weight_matrix + (1 - beta) * image_weight
    return weight_matrix


def run_spectral_clustering(adata: ad.AnnData, resolution: float = 0.5) -> ad.AnnData:
    """基于空间坐标的谱聚类（默认方法，无重依赖）。"""
    from scipy.spatial import distance
    from sklearn.cluster import SpectralClustering

    coords = adata.obsm["spatial"]
    dist_mat = distance.squareform(distance.pdist(coords))
    adj = np.exp(-dist_mat ** 2 / (2 * 100 ** 2))
    np.fill_diagonal(adj, 0)

    n_clusters = int(resolution * 10) if resolution < 1 else max(2, int(resolution))
    n_clusters = max(2, min(n_clusters, adata.n_obs - 1, 20))
    clustering = SpectralClustering(
        n_clusters=n_clusters, affinity="precomputed", random_state=42, assign_labels="kmeans"
    ).fit_predict(adj)
    adata.obs["spatial_domain"] = clustering.astype(str)
    adata.uns["spatial_domain_method"] = "spectral_clustering"
    return adata