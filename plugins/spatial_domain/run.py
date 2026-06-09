from __future__ import annotations

# plugins/spatial_domain/run.py
import scanpy as sc
import anndata as ad
import numpy as np
from scipy.spatial import distance
import warnings

def calculate_adj_matrix(x, y, x_bins=None, y_bins=None, image=None, beta=0.5, alpha=0.1):
    """
    计算空间邻接矩阵

    Parameters:
    -----------
    x, y : array-like
        空间坐标
    x_bins, y_bins : int, optional
        组织图像的像素binning因子
    image : ndarray, optional
        组织图像
    beta : float
        距离权重参数
    alpha : float
        图像权重参数

    Returns:
    --------
    adj : sparse matrix
        邻接矩阵
    """
    # 计算欧氏距离矩阵
    n = len(x)
    dist_mat = np.zeros((n, n))
    for i in range(n):
        dist_mat[i, :] = np.sqrt((x[i] - x) ** 2 + (y[i] - y) ** 2)

    # 计算距离权重
    # 使用高斯核
    sigma = np.median(dist_mat[dist_mat > 0])
    weight_matrix = np.exp(-dist_mat ** 2 / (2 * sigma ** 2))
    np.fill_diagonal(weight_matrix, 0)

    # 如果有图像，使用图像权重
    if image is not None and x_bins is not None and y_bins is not None:
        # 基于图像纹理计算额外权重
        image_weight = np.exp(-alpha * image)
        weight_matrix = beta * weight_matrix + (1 - beta) * image_weight

    return weight_matrix


def prep_spagnn(adj, p):
    """
    预处理邻接矩阵用于SPAGNN

    Parameters:
    -----------
    adj : sparse matrix
        邻接矩阵
    p : float
        dropout概率

    Returns:
    --------
    adj : sparse matrix
        预处理后的邻接矩阵
    """
    adj = adj - np.diag(np.diag(adj))
    adj = adj + np.eye(adj.shape[0])

    # 添加随机dropout边的效果
    adj = adj * (1 - p) + np.eye(adj.shape[0]) * p

    # 行归一化
    rowsum = np.array(adj.sum(1))
    d_inv = np.power(rowsum, -0.5).flatten()
    d_inv[np.isinf(d_inv)] = 0.
    d_mat_inv = np.diag(d_inv)
    adj = d_mat_inv @ adj @ d_mat_inv

    return adj


def train_spagnn(adj, X, n_clusters, alpha=0.5, hidden_dims=[128, 64],
                 epochs=200, learning_rate=0.01, random_state=42):
    """
    训练SPAGNN模型进行空间域识别

    Parameters:
    -----------
    adj : array-like
        预处理后的邻接矩阵
    X : array-like
        节点特征矩阵 (基因表达)
    n_clusters : int
        聚类数量
    alpha : float
        平滑因子
    hidden_dims : list
        隐藏层维度
    epochs : int
        训练轮数
    learning_rate : float
        学习率
    random_state : int
        随机种子

    Returns:
    --------
    z : array
        节点的嵌入表示
    cluster_result : array
        聚类结果
    """
    try:
        import torch
        import torch.nn.functional as F
        from torch import nn
    except ImportError:
        raise ImportError("PyTorch is required for SpaGCN. Install with: pip install torch")

    np.random.seed(random_state)
    torch.manual_seed(random_state)

    n_genes, n_nodes = X.shape[1], X.shape[0]

    # 转换为PyTorch稀疏矩阵
    adj = torch.FloatTensor(adj)
    X = torch.FloatTensor(X)

    # 定义SPAGNN模型
    class SPAGNN(nn.Module):
        def __init__(self, n_genes, hidden_dims, alpha):
            super(SPAGNN, self).__init__()
            self.alpha = alpha

            layers = []
            in_dim = n_genes
            for hidden_dim in hidden_dims:
                layers.append(nn.Linear(in_dim, hidden_dim))
                layers.append(nn.ReLU())
                in_dim = hidden_dim
            layers.append(nn.Linear(in_dim, hidden_dims[-1]))

            self.encoder = nn.Sequential(*layers)
            self.decoder = nn.Sequential(
                nn.Linear(hidden_dims[-1], hidden_dims[-1]),
                nn.ReLU(),
                nn.Linear(hidden_dims[-1], n_genes)
            )

        def forward(self, adj, X):
            # 图卷积
            h = self.encoder(X)
            h = torch.spmm(adj, h)
            h = F.relu(h)

            # 解码重建
            recon = self.decoder(h)

            # 拉普拉斯平滑
            smoothed = self.alpha * torch.spmm(adj, h) + (1 - self.alpha) * h

            return smoothed, recon, h

    # 初始化模型
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = SPAGNN(n_genes, hidden_dims, alpha).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    adj = adj.to(device)
    X = X.to(device)

    # 训练
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        smoothed, recon, h = model(adj, X)

        # 重建损失
        loss = F.mse_loss(recon, X)

        loss.backward()
        optimizer.step()

        if (epoch + 1) % 50 == 0:
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {loss.item():.4f}")

    # 获取嵌入
    model.eval()
    with torch.no_grad():
        _, _, z = model(adj, X)
        z = z.cpu().numpy()

    # 使用K-means进行聚类
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    cluster_result = kmeans.fit_predict(z)

    return z, cluster_result


def run_spagcn(adata, resolution=0.5, n_pcs=50, alpha=0.5, epochs=200,
                hidden_dims=[128, 64], p=0.05, target_sum=1e4):
    """
    使用SpaGCN进行空间域识别

    Parameters:
    -----------
    adata : AnnData
        空间转录组数据
    resolution : float
        聚类分辨率，用于确定聚类数量
    n_pcs : int
        PCA维度
    alpha : float
        平滑因子
    epochs : int
        训练轮数
    hidden_dims : list
        隐藏层维度
    p : float
        dropout概率
    target_sum : float
        归一化目标

    Returns:
    --------
    adata : AnnData
        添加了spatial_domain注释的AnnData
    """
    print("Running SpaGCN spatial domain identification...")

    # 获取空间坐标
    if "spatial" not in adata.obsm:
        raise ValueError("Spatial coordinates not found in adata.obsm['spatial']")

    x = adata.obsm["spatial"][:, 0]
    y = adata.obsm["spatial"][:, 1]

    # 计算邻接矩阵
    print("Computing adjacency matrix...")
    adj = calculate_adj_matrix(x, y)

    # 预处理用于SPAGNN
    print("Preprocessing adjacency matrix...")
    adj = prep_spagnn(adj, p)

    # 准备基因表达矩阵
    print("Preparing gene expression matrix...")
    X = adata.X

    # 如果是稀疏矩阵，转换为密集矩阵
    if hasattr(X, 'toarray'):
        X = X.toarray()
    else:
        X = np.array(X)

    # PCA降维以减少计算量
    if X.shape[1] > n_pcs:
        from sklearn.decomposition import PCA
        pca = PCA(n_components=n_pcs, random_state=42)
        X_pca = pca.fit_transform(X)
        print(f"Reduced to {n_pcs} PCs")
    else:
        X_pca = X

    # 确定聚类数量
    n_clusters = int(resolution * 10) if resolution < 1 else max(2, int(resolution))
    n_clusters = max(2, min(n_clusters, 20))
    print(f"Number of clusters: {n_clusters}")

    # 训练SPAGNN
    print("Training SPAGNN model...")
    try:
        z, cluster_result = train_spagnn(
            adj, X_pca, n_clusters=n_clusters,
            alpha=alpha, hidden_dims=hidden_dims,
            epochs=epochs, random_state=42
        )
    except ImportError as e:
        print(f"PyTorch not available: {e}")
        print("Falling back to spectral clustering...")
        return run_spectral_clustering(adata, resolution, n_pcs)

    # 保存结果
    adata.obs["spatial_domain"] = cluster_result.astype(str)
    adata.obs["spatial_domain_z"] = list(z)
    adata.uns["spatial_domain_method"] = "spagcn"
    adata.uns["spatial_domain_n_clusters"] = n_clusters

    print(f"SpaGCN completed. Found {n_clusters} spatial domains.")

    return adata


def run_spectral_clustering(adata, resolution=0.5, n_pcs=50):
    """
    使用谱聚类进行空间域识别（备选方案）
    """
    from sklearn.cluster import SpectralClustering

    x = adata.obsm["spatial"][:, 0]
    y = adata.obsm["spatial"][:, 1]

    # 计算距离矩阵
    coords = np.column_stack([x, y])
    dist_mat = distance.squareform(distance.pdist(coords))

    # 高斯核邻接矩阵
    adj = np.exp(-dist_mat ** 2 / (2 * 100 ** 2))
    np.fill_diagonal(adj, 0)

    # 聚类数量
    n_clusters = int(resolution * 10) if resolution < 1 else max(2, int(resolution))
    n_clusters = max(2, min(n_clusters, 20))

    print(f"Running spectral clustering with {n_clusters} clusters...")
    clustering = SpectralClustering(
        n_clusters=n_clusters,
        affinity='precomputed',
        random_state=42,
        assign_labels='kmeans'
    ).fit_predict(adj)

    adata.obs["spatial_domain"] = clustering.astype(str)
    adata.uns["spatial_domain_method"] = "spectral_clustering"

    return adata


def run_bayespace(adata, resolution=0.5):
    """
    使用BayesSpace进行空间域识别

    注意：BayesSpace需要R环境。完整实现请参考：
    https://github.com/edward130603/BayesSpace

    Parameters:
    -----------
    adata : AnnData
        空间转录组数据
    resolution : float
        分辨率参数

    Returns:
    --------
    adata : AnnData
        添加了spatial_domain注释的AnnData
    """
    warnings.warn(
        "BayesSpace requires R environment. "
        "To use BayesSpace in R:\n"
        "  library(BayesSpace)\n"
        "  data <- Seurat::UpdateSeuratObject(data)\n"
        "  data <- spatialEnhance(data, platform='Visium', ...)\n"
        "Using Louvain clustering as placeholder."
    )

    if 'X_pca' not in adata.obsm:
        sc.tl.pca(adata, n_comps=50)
    if '_neighbors' not in adata.uns:
        sc.pp.neighbors(adata, n_neighbors=15, n_pcs=50)

    sc.tl.louvain(adata, resolution=resolution)
    adata.obs["spatial_domain"] = adata.obs["louvain"]
    adata.uns["spatial_domain_method"] = "bayespace_placeholder"

    return adata


def run_stlearn(adata, resolution=0.5):
    """
    使用STlearn进行空间域识别

    注意：STlearn需要额外安装。安装方式：
    pip install stlearn

    Parameters:
    -----------
    adata : AnnData
        空间转录组数据
    resolution : float
        分辨率参数

    Returns:
    --------
    adata : AnnData
        添加了spatial_domain注释的AnnData
    """
    try:
        import stlearn
    except ImportError:
        warnings.warn(
            "STlearn not installed. Install with: pip install stlearn"
            "Using Louvain clustering as placeholder."
        )
        if 'X_pca' not in adata.obsm:
            sc.tl.pca(adata, n_comps=50)
        if 'neighbors' not in adata.uns:
            sc.pp.neighbors(adata, n_neighbors=15, n_pcs=50)
        sc.tl.louvain(adata, resolution=resolution)
        adata.obs["spatial_domain"] = adata.obs["louvain"]
        adata.uns["spatial_domain_method"] = "stlearn_placeholder"
        return adata

    # STlearn实现
    # 使用STlearn的SME方法
    print("Running STlearn SME clustering...")
    adata = stlearn.tl.cci.cci(adata, neighbors_key='spatial_neighbors')
    adata = stlearn.tl.cluster.kmeans(adata, n_clusters=int(resolution * 10))

    adata.obs["spatial_domain"] = adata.obs["kmeans"]
    adata.uns["spatial_domain_method"] = "stlearn"

    return adata


# Snakemake script接口
if __name__ == "__snakemake__":
    input_file = snakemake.input[0]
    output_file = snakemake.output[0]
    method = snakemake.params["method"]
    params = snakemake.params["params"]

    adata = ad.read_h5ad(input_file)

    print(f"Running spatial domain analysis with method: {method}")
    print(f"Parameters: {params}")

    if method == "spagcn":
        adata = run_spagcn(adata, **params)
    elif method == "bayespace":
        adata = run_bayespace(adata, **params)
    elif method == "stlearn":
        adata = run_stlearn(adata, **params)
    else:
        raise ValueError(f"Unknown method: {method}")

    adata.write_h5ad(output_file)
    print(f"Results saved to {output_file}")
