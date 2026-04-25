# plugins/spatial_domain/run.py
import scanpy as sc
import anndata as ad
import numpy as np
from scipy.spatial import distance

def run_spagcn(adata, resolution=0.5, n_pcs=50):
    """使用SpaGCN进行空间域识别"""
    # 构建空间邻接图
    coords = adata.obsm["spatial"]

    # 计算距离矩阵
    dist_mat = distance.squareform(distance.pdist(coords))

    # 使用高斯核构建邻接矩阵
    adj = np.exp(-dist_mat ** 2 / (2 * 100 ** 2))
    np.fill_diagonal(adj, 0)

    # 简单的图分割 - 使用Leiden聚类在空间邻接图上
    if 'X_pca' not in adata.obsm:
        sc.tl.pca(adata, n_comps=n_pcs)

    # 将空间信息添加到邻居计算
    from sklearn.cluster import SpectralClustering

    # 使用空间邻接矩阵进行谱聚类
    n_clusters = int(resolution * 10) if resolution < 1 else int(resolution)
    n_clusters = max(2, min(n_clusters, 20))

    clustering = SpectralClustering(
        n_clusters=n_clusters,
        affinity='precomputed',
        random_state=42
    ).fit_predict(adj)

    adata.obs["spatial_domain"] = clustering.astype(str)

    return adata

def run_bayespace(adata, resolution=0.5):
    """使用BayesSpace进行空间域识别 - 占位实现"""
    # BayesSpace需要R环境，这里使用简化版本
    if 'spatial_domain' not in adata.obs:
        sc.tl.louvain(adata, resolution=resolution)
        adata.obs["spatial_domain"] = adata.obs["louvain"]
    return adata

def run_stlearn(adata, resolution=0.5):
    """使用STlearn进行空间域识别 - 占位实现"""
    if 'spatial_domain' not in adata.obs:
        sc.tl.louvain(adata, resolution=resolution)
        adata.obs["spatial_domain"] = adata.obs["louvain"]
    return adata

# Snakemake script接口
if __name__ == "__snakemake__":
    input_file = snakemake.input[0]
    output_file = snakemake.output[0]
    method = snakemake.params["method"]
    params = snakemake.params["params"]

    adata = ad.read_h5ad(input_file)

    if method == "spagcn":
        adata = run_spagcn(adata, **params)
    elif method == "bayespace":
        adata = run_bayespace(adata, **params)
    elif method == "stlearn":
        adata = run_stlearn(adata, **params)

    adata.write_h5ad(output_file)