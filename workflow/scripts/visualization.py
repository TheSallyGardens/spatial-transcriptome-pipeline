from __future__ import annotations

# workflow/scripts/visualization.py
import scanpy as sc
import squidpy as sq
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
from pathlib import Path

def plot_spatial_scatter(adata, color, output_file, title=None):
    """绘制空间散点图"""
    fig, ax = plt.subplots(figsize=(10, 10))
    if title is None:
        title = f"Spatial view - {color}"
    sc.pl.spatial(adata, color=color, ax=ax, show=False, title=title)
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()

def plot_umap(adata, color, output_file, title=None):
    """绘制UMAP图"""
    fig, ax = plt.subplots(figsize=(10, 10))
    if title is None:
        title = f"UMAP - {color}"
    sc.pl.umap(adata, color=color, ax=ax, show=False, title=title)
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()

def plot_cluster_composition(adata, groupby, output_file):
    """绘制聚类组成图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    sc.pl.rank_genes_groups_dotplot(adata, groupby=groupby, ax=ax, show=False)
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()

def plot_spatial_genes(adata, genes, output_file):
    """绘制空间基因表达图"""
    n_genes = len(genes)
    n_cols = min(3, n_genes)
    n_rows = (n_genes + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 5 * n_rows))
    if n_genes == 1:
        axes = [axes]
    else:
        axes = axes.flatten() if n_rows > 1 else axes

    for i, gene in enumerate(genes):
        if gene in adata.var_names:
            sc.pl.spatial(adata, color=[gene], ax=axes[i], show=False)

    # 隐藏空子图
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')

    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()

# Snakemake script接口
if __name__ == "__snakemake__":
    input_file = snakemake.input[0]
    output_file = snakemake.output[0]
    plot_type = snakemake.params["plot_type"]
    color_by = snakemake.params.get("color_by", "louvain")

    adata = sc.read_h5ad(input_file)

    # 确保输出目录存在
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    if plot_type == "spatial":
        plot_spatial_scatter(adata, color_by, output_file)
    elif plot_type == "umap":
        plot_umap(adata, color_by, output_file)
    elif plot_type == "spatial_genes":
        genes = snakemake.params.get("genes", adata.var_names[:5].tolist())
        plot_spatial_genes(adata, genes, output_file)