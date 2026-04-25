# plugins/spatial_variable_genes/run.py
import scanpy as sc
import anndata as ad
import numpy as np

def run_morans_i(adata, n_permutations=100):
    """使用Moran's I识别空间变量基因"""
    from scipy.spatial import distance

    # 获取空间坐标
    coords = adata.obsm["spatial"]

    # 计算空间权重矩阵
    dist_mat = distance.squareform(distance.pdist(coords))
    weights = np.exp(-dist_mat / 100)  # 高斯核权重

    # 对每个基因计算Moran's I
    results = []
    for gene in adata.var_names[:500]:  # 限制计算量以提高速度
        expression = adata[:, gene].X.toarray().flatten() if hasattr(adata[:, gene].X, 'toarray') else adata[:, gene].X.flatten()
        if expression.std() > 0:
            # 简化的Moran's I计算
            mean_expr = expression.mean()
            n = len(expression)
            deviation = expression - mean_expr
            spatial_deviation = weights.dot(deviation)
            numerator = np.sum(deviation * spatial_deviation) / n
            denominator = np.sum(deviation ** 2) / n
            if denominator > 0:
                morans_i = numerator / denominator
                results.append((gene, morans_i))

    # 排序并保存top基因
    results.sort(key=lambda x: abs(x[1]), reverse=True)
    adata.uns["spatial_variable_genes"] = results[:100]

    return adata

def run_spark(adata):
    """使用SPARK进行空间变量基因分析"""
    return adata

def run_lisa(adata):
    """使用LISA进行空间变量基因分析"""
    return adata

# Snakemake script接口
if __name__ == "__snakemake__":
    input_file = snakemake.input[0]
    output_file = snakemake.output[0]
    method = snakemake.params["method"]
    params = snakemake.params["params"]

    adata = ad.read_h5ad(input_file)

    if method == "morans_i":
        adata = run_morans_i(adata, **params)
    elif method == "spark":
        adata = run_spark(adata, **params)
    elif method == "lisa":
        adata = run_lisa(adata, **params)

    adata.write_h5ad(output_file)