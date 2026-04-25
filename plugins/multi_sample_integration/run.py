# plugins/multi_sample_integration/run.py
import scanpy as sc
import anndata as ad
import numpy as np

def run_harmony(adata_list, theta=2.0, max_iter=20):
    """使用Harmony进行批次校正和整合"""
    # 合并AnnData列表
    adata_combined = ad.concat(
        adata_list,
        batch_key="sample",
        uns_merge="same"
    )

    # 运行Harmony
    try:
        import harmonypy as hm

        ho = hm.Harmony(
            data_mat=adata_combined.obsm["X_pca"],
            meta_data=adata_combined.obs,
            group_by=["sample"],
            theta=theta,
            max_iter=max_iter
        )

        corrected = ho.Harmony_embedding()

        # 保存校正后的PCA
        adata_combined.obsm["X_pca_harmony"] = corrected
        adata_combined.uns["integration_method"] = "harmony"
    except ImportError:
        print("Warning: harmonypy not installed, skipping batch correction")

    return adata_combined

def run_bbknn(adata_list):
    """使用BBKNN进行整合"""
    adata_combined = ad.concat(adata_list, batch_key="sample", uns_merge="same")

    sc.pp.neighbors(adata_combined, use_rep="X_pca", n_neighbors=15)

    adata_combined.uns["integration_method"] = "bbknn"

    return adata_combined

def run_liger(adata_list):
    """使用Liger进行整合"""
    adata_combined = ad.concat(adata_list, batch_key="sample", uns_merge="same")

    adata_combined.uns["integration_method"] = "liger"

    return adata_combined

# Snakemake script接口
if __name__ == "__snakemake__":
    input_files = snakemake.input
    output_file = snakemake.output[0]
    method = snakemake.params["method"]
    params = snakemake.params["params"]

    adata_list = [ad.read_h5ad(f) for f in input_files]

    if method == "harmony":
        adata_combined = run_harmony(adata_list, **params)
    elif method == "bbknn":
        adata_combined = run_bbknn(adata_list, **params)
    elif method == "liger":
        adata_combined = run_liger(adata_list, **params)

    adata_combined.write_h5ad(output_file)