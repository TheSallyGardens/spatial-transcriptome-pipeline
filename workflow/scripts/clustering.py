from __future__ import annotations

# workflow/scripts/clustering.py
import scanpy as sc
import anndata as ad

def run_pca(adata, n_comps=50):
    sc.tl.pca(adata, n_comps=n_comps, svd_solver='arpack')
    return adata

def run_neighbors(adata, n_neighbors=15, n_pcs=50):
    sc.pp.neighbors(adata, n_neighbors=n_neighbors, n_pcs=n_pcs)
    return adata

def run_louvain(adata, resolution=0.5):
    if 'louvain' not in adata.obs:
        sc.tl.louvain(adata, resolution=resolution)
    return adata

def run_leiden(adata, resolution=0.5):
    if 'leiden' not in adata.obs:
        sc.tl.leiden(adata, resolution=resolution)
    return adata

# Snakemake script interface
if __name__ == "__snakemake__":
    input_file = snakemake.input[0]
    output_file = snakemake.output[0]
    rule_name = snakemake.rule

    adata = ad.read_h5ad(input_file)

    if rule_name == "run_pca":
        adata = run_pca(adata)
    elif rule_name == "run_neighbors":
        adata = run_neighbors(adata)
    elif rule_name == "run_clustering":
        adata = run_louvain(adata)
        adata = run_leiden(adata)

    adata.write_h5ad(output_file)