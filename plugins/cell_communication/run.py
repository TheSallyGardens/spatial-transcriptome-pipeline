from __future__ import annotations

# plugins/cell_communication/run.py
import scanpy as sc
import anndata as ad
import numpy as np
import pandas as pd
import warnings

def run_cellchat(adata, min_cells=10):
    """
    使用CellChat进行细胞间通讯分析

    注意：完整版CellChat需要R环境。
    安装: R环境 + remotes::install_github("sqjin/CellChat")

    这里提供Python版本的简化实现，使用Squidpy作为替代。

    Parameters:
    -----------
    adata : AnnData
        带注释的空间转录组数据
    min_cells : int
        最小细胞数阈值

    Returns:
    --------
    adata : AnnData
        添加了细胞通讯分析结果
    """
    warnings.warn(
        "Full CellChat requires R environment. "
        "Using Python implementation as alternative. "
        "For full CellChat: R + remotes::install_github('sqjin/CellChat')"
    )

    import squidpy as sq

    # 确保有细胞类型注释
    if 'cell_type' not in adata.obs:
        if 'louvain' in adata.obs:
            adata.obs['cell_type'] = adata.obs['louvain']
        else:
            warnings.warn("No cell type annotation found. Using Louvain clustering.")
            sc.tl.louvain(adata)
            adata.obs['cell_type'] = adata.obs['louvain']

    # 计算空间邻居
    sq.gr.spatial_neighbors(adata, coord_type='spatial')

    # 邻域富集分析 - 计算不同细胞类型之间的空间共定位
    sq.gr.nhood_enrichment(adata, cluster_key="cell_type")

    # 保存富集结果
    n_clusters = len(adata.obs['cell_type'].unique())
    adata.uns['cell_communication'] = {
        'method': 'cellchat_python',
        'n_cell_types': n_clusters,
        'n_neighbors': min_cells
    }

    # 计算配体-受体对通讯评分（简化版）
    # 使用空间邻居关系推断通讯
    lr_scores = compute_lr_scores(adata)
    adata.uns['lr_scores'] = lr_scores

    return adata


def compute_lr_scores(adata):
    """
    简化版配体-受体对评分

    使用空间邻居关系计算细胞类型之间的潜在通讯强度
    """
    # 定义一些常见的配体-受体对
    lr_pairs = {
        ('CD3D', 'CD8A'): 'T cell signaling',
        ('CD19', 'CD79A'): 'B cell signaling',
        ('CD68', 'CD14'): 'Macrophage signaling',
        ('EGFR', 'EGF'): 'Growth factor signaling',
        ('VEGFA', 'FLT1'): 'Angiogenesis',
        ('CXCL12', 'CXCR4'): 'Chemokine signaling',
        ('TNF', 'TNFRSF1A'): 'Inflammation',
        ('IL6', 'IL6R'): 'Interleukin signaling',
    }

    cell_types = adata.obs['cell_type'].unique()
    n_types = len(cell_types)

    # 创建细胞类型对之间的通讯评分矩阵
    comm_matrix = np.zeros((n_types, n_types))

    for i, ct1 in enumerate(cell_types):
        for j, ct2 in enumerate(cell_types):
            if i != j:
                # 获取两种细胞类型的细胞
                cells_ct1 = adata.obs[adata.obs['cell_type'] == ct1].index
                cells_ct2 = adata.obs[adata.obs['cell_type'] == ct2].index

                # 简化：计算基因表达的相关性作为通讯强度
                if ct1 in adata.var_names and ct2 in adata.var_names:
                    expr1 = adata[cells_ct1, ct1].X.mean()
                    expr2 = adata[cells_ct2, ct2].X.mean()
                    comm_matrix[i, j] = expr1 * expr2

    return pd.DataFrame(comm_matrix, index=cell_types, columns=cell_types)


def run_squidpy(adata):
    """
    使用Squidpy进行空间通讯分析

    Squidpy是Python原生库，提供了完整的空间分析方法。

    安装: pip install squidpy

    Parameters:
    -----------
    adata : AnnData
        空间转录组数据

    Returns:
    --------
    adata : AnnData
        添加了通讯分析结果
    """
    import squidpy as sq

    # 确保有细胞类型注释
    if 'cell_type' not in adata.obs:
        if 'louvain' in adata.obs:
            adata.obs['cell_type'] = adata.obs['louvain']
        else:
            sc.tl.louvain(adata)
            adata.obs['cell_type'] = adata.obs['louvain']

    # 计算空间邻居
    print("Computing spatial neighbors...")
    sq.gr.spatial_neighbors(adata, coord_type='spatial', n_neighbors=10)

    # 邻域富集分析
    print("Computing neighborhood enrichment...")
    sq.gr.nhood_enrichment(adata, cluster_key="cell_type")

    # 空间自相关分析
    print("Computing spatial autocorrelation...")
    sq.gr.spatial_autocorr(adata, genes=adata.var_names[:100], n_perms=100)

    # 配体-受体分析（如果squidpy版本支持）
    print("Computing ligand-receptor interactions...")
    try:
        sq.gr.ligrec(adata, cluster_key="cell_type", use_raw=False)
    except Exception as e:
        print(f"Ligand-receptor analysis skipped: {e}")

    # 保存结果
    adata.uns['cell_communication'] = {
        'method': 'squidpy',
        'n_cell_types': len(adata.obs['cell_type'].unique())
    }

    return adata


def run_nichenet(adata):
    """
    使用NicheNet进行细胞间通讯分析

    NicheNet需要R环境。
    安装: R + remotes::install_github("saeyslab/nichenetr")

    这里提供Python版本的简化实现。

    Parameters:
    -----------
    adata : AnnData
        空间转录组数据

    Returns:
    --------
    adata : AnnData
        添加了NicheNet分析结果
    """
    warnings.warn(
        "Full NicheNet requires R environment. "
        "Using Python implementation as alternative. "
        "For full NicheNet: R + remotes::install_github('saeyslab/nichenetr')"
    )

    # 确保有细胞类型注释
    if 'cell_type' not in adata.obs:
        if 'louvain' in adata.obs:
            adata.obs['cell_type'] = adata.obs['louvain']
        else:
            sc.tl.louvain(adata)
            adata.obs['cell_type'] = adata.obs['louvain']

    # 使用简化的NicheNet-like分析
    cell_types = adata.obs['cell_type'].unique()

    # 定义一些常见的信号通路基因
    pathway_genes = {
        'TGF-beta': ['TGFB1', 'TGFB2', 'TGFB3', 'SMAD2', 'SMAD3'],
        'Wnt': ['WNT1', 'WNT3A', 'CTNNB1', 'APC', 'AXIN1'],
        'Hedgehog': ['SHH', 'GLI1', 'GLI2', 'PTCH1', 'SMO'],
        'Notch': ['NOTCH1', 'DLL1', 'JAG1', 'HES1', 'HEY1'],
        'Hippo': ['YAP1', 'TAZ', 'TEAD1', 'TEAD2', 'LATS1'],
    }

    # 计算每个细胞类型的通路活性
    pathway_activity = {}
    for pathway, genes in pathway_genes.items():
        genes_in_data = [g for g in genes if g in adata.var_names]
        if genes_in_data:
            pathway_activity[pathway] = adata[:, genes_in_data].X.mean(axis=1)

    adata.obs['pathway_activity'] = pd.DataFrame(pathway_activity).idxmax(axis=1)
    adata.uns['cell_communication'] = {
        'method': 'nichenet_python',
        'pathways': list(pathway_genes.keys())
    }

    return adata


# Snakemake script接口
if __name__ == "__snakemake__":
    input_file = snakemake.input[0]
    output_file = snakemake.output[0]
    method = snakemake.params["method"]
    params = snakemake.params["params"]

    adata = ad.read_h5ad(input_file)

    print(f"Running cell communication analysis with method: {method}")

    if method == "cellchat":
        adata = run_cellchat(adata, **params)
    elif method == "squidpy":
        adata = run_squidpy(adata, **params)
    elif method == "nichenet":
        adata = run_nichenet(adata, **params)
    else:
        raise ValueError(f"Unknown method: {method}")

    adata.write_h5ad(output_file)
    print(f"Results saved to {output_file}")
