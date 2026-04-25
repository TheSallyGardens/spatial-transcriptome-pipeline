# plugins/trajectory/run.py
import scanpy as sc
import anndata as ad
import numpy as np
import pandas as pd
import warnings


def run_paga(adata, cluster_res=0.5, paga_thresh=0.1):
    """
    使用PAGA进行轨迹分析

    PAGA (Partition-based Graph Abstraction) 是Scanpy内置的轨迹分析方法，
    可以推断细胞之间的连接关系和发育轨迹。

    安装: pip install scanpy (已包含)

    Parameters:
    -----------
    adata : AnnData
        带聚类结果的空间转录组数据
    cluster_res : float
        聚类分辨率
    paga_thresh : float
        PAGA连接的阈值

    Returns:
    --------
    adata : AnnData
        添加了PAGA轨迹结果
    """
    # 确保有聚类结果
    if 'louvain' not in adata.obs and 'leiden' not in adata.obs:
        print(f"Running clustering with resolution={cluster_res}...")
        sc.tl.louvain(adata, resolution=cluster_res)

    cluster_key = 'louvain' if 'louvain' in adata.obs else 'leiden'

    # 确保有UMAP坐标
    if 'X_umap' not in adata.obsm:
        if 'X_pca' not in adata.obsm:
            sc.tl.pca(adata, n_comps=50)
        sc.pp.neighbors(adata, n_neighbors=15, n_pcs=50)
        sc.tl.umap(adata)

    # 运行PAGA
    print("Running PAGA trajectory analysis...")
    sc.tl.paga(adata, groups=cluster_key, threshold=paga_thresh)

    # 使用PAGA初始化UMAP
    sc.tl.umap(adata, init_pos="paga")

    # 保存结果
    adata.uns['trajectory'] = {
        'method': 'paga',
        'groups': cluster_key,
        'threshold': paga_thres
    }

    # 计算轨迹分化时间（简化版）
    compute_pseudotime(adata, cluster_key)

    return adata


def compute_pseudotime(adata, cluster_key='louvain'):
    """
    计算伪时间（简化版PAGA路径分析）

    基于PAGA图计算每个细胞的伪时间值
    """
    # 获取PAGA连接矩阵
    if 'paga' not in adata.uns:
        return

    # 简化：使用UMAP坐标计算伪时间
    # 以UMAP最左端的细胞为起点
    umap_coords = adata.obsm['X_umap']
    start_point = umap_coords[:, 0].min()

    # 计算每个细胞到起点的距离
    distances = umap_coords[:, 0] - start_point
    adata.obs['pseudotime'] = distances / distances.max()

    adata.uns['trajectory']['has_pseudotime'] = True


def run_monocle(adata):
    """
    使用Monocle3进行轨迹分析

    Monocle3是专门的单细胞轨迹分析工具，需要CellDataSet格式。

    完整版安装:
    - R: install.packages('monocle3')
    - Python: pip install monocle3

    这里提供Python版本的简化实现。

    Parameters:
    -----------
    adata : AnnData
        空间转录组数据

    Returns:
    --------
    adata : AnnData
        添加了Monocle3轨迹结果
    """
    try:
        import monocle3 as mc
        HAS_MONOCLE3 = True
    except ImportError:
        HAS_MONOCLE3 = False
        warnings.warn(
            "Monocle3 not installed. Using PAGA-based trajectory instead. "
            "To install Monocle3: pip install monocle3"
        )

    if HAS_MONOCLE3:
        # 使用完整的Monocle3流程
        print("Running Monocle3 trajectory analysis...")

        # 创建CellDataSet
        cds = mc.ti.monocle3.CellDataSet(adata.X.T)

        # 设置空间坐标
        cds.dim_reduce = adata.obsm

        # 轨迹分析
        cds = mc.tl.learn_graph(cds)

        # 找起点
        cds = mc.tl.find_growth_rate(cds)

        # 将结果映射回AnnData
        adata.obs['monocle_state'] = [str(s) for s in cds.states]
        adata.obs['monocle_pseudotime'] = cds.pseudotime

        adata.uns['trajectory'] = {
            'method': 'monocle3',
            'n_states': len(cds.states.unique())
        }
    else:
        # 降级到PAGA
        return run_paga(adata)

    return adata


def run_st_trajectory(adata, n_components=3):
    """
    使用ST trajectory进行空间轨迹分析

    ST trajectory是专门为空间转录组设计的轨迹分析方法，
    可以考虑空间连续性进行轨迹推断。

    这里提供简化版实现，基于空间连续性和表达相似性。

    Parameters:
    -----------
    adata : AnnData
        空间转录组数据
    n_components : int
        PCA降维维度

    Returns:
    --------
    adata : AnnData
        添加了空间轨迹分析结果
    """
    from scipy.spatial import distance
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans

    print("Running ST trajectory analysis...")

    # 确保有空间坐标
    if 'spatial' not in adata.obsm:
        raise ValueError("Spatial coordinates required for ST trajectory analysis")

    coords = adata.obsm['spatial']

    # 确保有基因表达矩阵
    if 'X_pca' not in adata.obsm:
        if adata.X.shape[1] > n_components:
            pca = PCA(n_components=n_components)
            adata.obsm['X_pca_trajectory'] = pca.fit_transform(adata.X.toarray() if hasattr(adata.X, 'toarray') else adata.X)
        else:
            adata.obsm['X_pca_trajectory'] = adata.X

    # 构建空间距离加权图
    print("Building spatial neighbor graph...")
    dist_mat = distance.squareform(distance.pdist(coords))

    # 高斯核权重
    sigma = np.median(dist_mat[dist_mat > 0])
    spatial_weights = np.exp(-dist_mat ** 2 / (2 * sigma ** 2))
    np.fill_diagonal(spatial_weights, 0)

    # 基于空间权重和表达相似性构建轨迹图
    expr_dist = distance.squareform(distance.pdist(adata.obsm['X_pca_trajectory']))
    expr_weights = np.exp(-expr_dist ** 2 / (2 * expr_dist.mean() ** 2))

    # 综合权重
    combined_weights = 0.5 * spatial_weights + 0.5 * expr_weights

    # 使用谱嵌入进行轨迹分析
    from sklearn.manifold import SpectralEmbedding

    se = SpectralEmbedding(n_components=n_components, affinity='precomputed', random_state=42)
    trajectory_embedding = se.fit_transform(combined_weights)

    adata.obsm['X_trajectory'] = trajectory_embedding

    # 聚类轨迹状态
    n_trajectory_states = 3  # 可以根据数据调整
    kmeans = KMeans(n_clusters=n_trajectory_states, random_state=42)
    trajectory_states = kmeans.fit_predict(trajectory_embedding)

    adata.obs['trajectory_state'] = trajectory_states.astype(str)

    # 计算空间伪时间
    start_coords = coords[np.argmin(coords[:, 0])]
    spatial_pseudotime = np.sqrt(((coords - start_coords) ** 2).sum(axis=1))
    spatial_pseudotime = spatial_pseudotime / spatial_pseudotime.max()
    adata.obs['spatial_pseudotime'] = spatial_pseudotime

    # 识别轨迹起点和终点
    trajectory_graph = build_trajectory_graph(trajectory_embedding, trajectory_states)
    adata.uns['trajectory'] = {
        'method': 'st_trajectory',
        'n_states': n_trajectory_states,
        'trajectory_graph': trajectory_graph
    }

    return adata


def build_trajectory_graph(embedding, states):
    """
    构建轨迹图，表示不同状态之间的连接关系

    Parameters:
    -----------
    embedding : array
        轨迹嵌入
    states : array
        轨迹状态标签

    Returns:
    --------
    graph : dict
        轨迹图
    """
    from scipy.spatial.distance import cdist

    unique_states = np.unique(states)
    n_states = len(unique_states)

    # 计算每个状态的中心
    state_centers = np.array([
        embedding[states == s].mean(axis=0) for s in unique_states
    ])

    # 计算状态之间的距离
    state_dist = cdist(state_centers, state_centers)

    # 构建连接（使用KNN）
    graph = {}
    for i, s1 in enumerate(unique_states):
        distances = state_dist[i]
        # 找到最近的3个邻居（排除自己）
        neighbors = np.argsort(distances)[1:4]
        graph[str(s1)] = {
            'center': state_centers[i].tolist(),
            'next_states': [str(unique_states[n]) for n in neighbors[:2]]
        }

    return graph


# Snakemake script接口
if __name__ == "__snakemake__":
    input_file = snakemake.input[0]
    output_file = snakemake.output[0]
    method = snakemake.params["method"]
    params = snakemake.params["params"]

    adata = ad.read_h5ad(input_file)

    print(f"Running trajectory analysis with method: {method}")

    if method == "paga":
        adata = run_paga(adata, **params)
    elif method == "monocle":
        adata = run_monocle(adata, **params)
    elif method == "st_trajectory":
        adata = run_st_trajectory(adata, **params)
    else:
        raise ValueError(f"Unknown method: {method}")

    adata.write_h5ad(output_file)
    print(f"Results saved to {output_file}")
