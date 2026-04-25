# plugins/trajectory/run.py
import scanpy as sc
import anndata as ad

def run_paga(adata, cluster_res=0.5):
    """使用PAGA进行轨迹分析"""
    # 需要已有聚类结果
    if 'louvain' not in adata.obs:
        sc.tl.louvain(adata, resolution=cluster_res)

    sc.tl.paga(adata, groups="louvain")

    # 初始化UMAP用于轨迹可视化
    sc.tl.umap(adata, init_pos="paga")

    adata.uns["trajectory_method"] = "paga"

    return adata

def run_monocle(adata):
    """使用Monocle3进行轨迹分析"""
    # 需要CellDataSet对象 - 这里是占位实现
    return adata

def run_st_trajectory(adata):
    """使用ST trajectory进行空间轨迹分析"""
    return adata

# Snakemake script接口
if __name__ == "__snakemake__":
    input_file = snakemake.input[0]
    output_file = snakemake.output[0]
    method = snakemake.params["method"]
    params = snakemake.params["params"]

    adata = ad.read_h5ad(input_file)

    if method == "paga":
        adata = run_paga(adata, **params)
    elif method == "monocle":
        adata = run_monocle(adata, **params)
    elif method == "st_trajectory":
        adata = run_st_trajectory(adata, **params)

    adata.write_h5ad(output_file)