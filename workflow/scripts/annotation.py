from __future__ import annotations

# workflow/scripts/annotation.py
import scanpy as sc
import anndata as ad

def annotate_with_markers(adata, markers):
    """使用标记基因进行注释"""
    for cell_type, genes in markers.items():
        # 检查基因是否在数据中
        genes_in_data = [g for g in genes if g in adata.var_names]
        if genes_in_data:
            # 计算每个细胞的标记基因平均表达
            adata.obs[f'{cell_type}_score'] = adata[:, genes_in_data].X.mean(axis=1)

    # 基于最高表达的标记基因分配细胞类型
    if 'cell_type' not in adata.obs:
        marker_cols = [c for c in adata.obs.columns if c.endswith('_score')]
        if marker_cols:
            scores = adata.obs[marker_cols].values
            cell_types = [col.replace('_score', '') for col in marker_cols]
            adata.obs['cell_type'] = [cell_types[i] for i in scores.argmax(axis=1)]
        else:
            adata.obs['cell_type'] = 'Unknown'

    return adata

# Snakemake script interface
if __name__ == "__snakemake__":
    input_file = snakemake.input[0]
    output_file = snakemake.output[0]

    adata = ad.read_h5ad(input_file)

    # 默认标记基因
    marker_genes = {
        "T cells": ["CD3D", "CD3E", "CD8A"],
        "B cells": ["CD19", "CD79A", "MS4A1"],
        "Macrophages": ["CD68", "CD14", "FCGR3A"],
        "NK cells": ["GNLY", "NKG7", "KLRD1"],
        "Epithelial": ["EPCAM", "KRT18", "KRT19"],
    }

    adata = annotate_with_markers(adata, marker_genes)
    adata.write_h5ad(output_file)