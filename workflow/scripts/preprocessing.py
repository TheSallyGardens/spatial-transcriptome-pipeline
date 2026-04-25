# workflow/scripts/preprocessing.py
import scanpy as sc
import anndata as ad

def filter_cells_and_genes(adata, min_genes=200, min_cells=50):
    """质控过滤"""
    sc.pp.filter_cells(adata, min_genes=min_genes)
    sc.pp.filter_genes(adata, min_cells=min_cells)
    return adata

def normalize_total(adata, target_sum=1e4):
    """Library size normalization"""
    sc.pp.normalize_total(adata, target_sum=target_sum)
    return adata

def log_transform(adata):
    """Log转换"""
    sc.pp.log1p(adata)
    return adata

def highly_variable_genes(adata, n_top_genes=2000):
    """识别高变异基因"""
    sc.pp.highly_variable_genes(adata, n_top_genes=n_top_genes)
    return adata

def scale_data(adata):
    """数据缩放"""
    sc.pp.scale(adata, max_value=10)
    return adata

# Snakemake script接口
if __name__ == "__snakemake__":
    input_file = snakemake.input[0]
    output_file = snakemake.output[0]
    sample_config = config["samples"][snakemake.wildcards["sample"]]

    adata = ad.read_h5ad(input_file)
    filter_config = sample_config.get("config", {})

    adata = filter_cells_and_genes(
        adata,
        min_genes=filter_config.get("min_genes", 200),
        min_cells=filter_config.get("min_cells", 50)
    )
    adata = normalize_total(adata)
    adata = log_transform(adata)
    adata = highly_variable_genes(adata)

    adata.write_h5ad(output_file)