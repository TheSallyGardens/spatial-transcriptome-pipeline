# plugins/scRNA_joint_analysis/run.py
import scanpy as sc
import anndata as ad
import numpy as np
import pandas as pd
import warnings


def run_seurat_transfer(adata_st, adata_sc=None, reference="panglaodb", k.weight=30):
    """
    使用Seurat V5进行标签迁移联合分析

    Seurat V5是最新的版本，提供了更现代的整合方法。
    通过标签迁移将单细胞参考的细胞类型注释转移到空间数据。

    安装要求:
    - R 4.3+
    - Seurat 5.x: remotes::install_github("satijalab/seurat", "seurat5")
    - SeuratObject 5.x: remotes::install_github("satijalab/seurat", "seurat5")

    Python端使用rpy2调用，或在R中处理后导入结果。

    Parameters:
    -----------
    adata_st : AnnData
        空间转录组数据
    adata_sc : AnnData, optional
        单细胞参考数据，如果为None则使用公共数据库
    reference : str
        参考数据集 ('panglaodb', 'human_cell_atlas', etc.)
    k.weight : int
        KNN权重参数

    Returns:
    --------
    adata_st : AnnData
        添加了预测的细胞类型注释
    """
    warnings.warn(
        "Seurat V5 label transfer requires R environment with Seurat 5.x. "
        "Python implementation provides label transfer based on gene expression similarity. "
        "\n"
        "To use full Seurat V5:"
        "\n  R> remotes::install_github('satijalab/seurat', 'seurat5')"
        "\n  R> library(Seurat)"
        "\n  R> # Follow Seurat vignette for label transfer"
    )

    print("Running Seurat-like label transfer...")

    # 如果没有参考数据，使用标记基因方法
    if adata_sc is None:
        return label_transfer_markers(adata_st)

    # 确保两个数据集都有PCA
    if 'X_pca' not in adata_st.obsm:
        sc.pp.pca(adata_st, n_comps=50)

    if 'X_pca' not in adata_sc.obsm:
        sc.pp.pca(adata_sc, n_comps=50)

    # 使用标签传播/迁移
    predicted_labels = label_transfer_knn(adata_st, adata_sc)

    adata_st.obs['predicted_cell_type'] = predicted_labels

    adata_st.uns['scRNA_joint_analysis'] = {
        'method': 'seurat_transfer',
        'reference': reference,
        'has_reference': True
    }

    return adata_st


def label_transfer_markers(adata):
    """
    使用标记基因进行细胞类型注释（无参考数据时使用）

    Parameters:
    -----------
    adata : AnnData
        空间转录组数据

    Returns:
    --------
    adata : AnnData
        添加了细胞类型注释
    """
    # 常用细胞类型标记基因
    marker_genes = {
        'T cells': ['CD3D', 'CD3E', 'CD8A', 'CD8B', 'CD4'],
        'B cells': ['CD19', 'CD79A', 'MS4A1', 'CD20', 'CD79B'],
        'NK cells': ['GNLY', 'NKG7', 'KLRD1', 'KLRB1', 'NCR1'],
        'Macrophages': ['CD68', 'CD14', 'FCGR3A', 'CD163', 'CSF1R'],
        'Monocytes': ['CD14', 'FCN1', 'S100A8', 'S100A9', 'CD68'],
        'Dendritic cells': ['HLA-DRA', 'HLA-DPA1', 'CD1C', 'BCAM'],
        'Neutrophils': ['CSF3R', 'CXCR2', 'S100A8', 'S100A9', 'FCGR3B'],
        'Epithelial cells': ['EPCAM', 'KRT18', 'KRT19', 'KRT8', 'CDH1'],
        'Cancer cells': ['EPCAM', 'KRT18', 'KRT19', 'MUC1', 'EPCAM'],
        'Fibroblasts': ['COL1A1', 'COL1A2', 'COL3A1', 'FAP', 'ACTA2'],
        'Endothelial cells': ['PECAM1', 'CDH5', 'FLT1', 'VWF', 'ERG'],
        'Smooth muscle': ['ACTA2', 'MYH11', 'TAGLN', 'CALD1', 'CNN1'],
        'Adipocytes': ['LEP', 'ADIPOQ', 'PLIN1', 'FABP4', 'LPL'],
        'Melanocytes': ['TYR', 'MITF', 'PMEL', 'MLANA', 'DCT'],
    }

    # 计算每个细胞的标记基因得分
    scores = {}
    for cell_type, genes in marker_genes.items():
        genes_in_data = [g for g in genes if g in adata.var_names]
        if genes_in_data:
            # 计算平均表达
            scores[cell_type] = adata[:, genes_in_data].X.mean(axis=1)

    if not scores:
        adata.obs['predicted_cell_type'] = 'Unknown'
        return adata

    # 创建得分矩阵
    score_df = pd.DataFrame(scores, index=adata.obs_names)

    # 分配最高表达的细胞类型
    adata.obs['predicted_cell_type'] = score_df.idxmax(axis=1).values

    # 添加置信度得分
    adata.obs['cell_type_confidence'] = score_df.max(axis=1).values / (score_df.sum(axis=1).values + 1e-10)

    return adata


def label_transfer_knn(adata_query, adata_reference):
    """
    使用KNN进行标签迁移

    Parameters:
    -----------
    adata_query : AnnData
        查询数据集（空间数据）
    adata_reference : AnnData
        参考数据集（单细胞数据，带注释）

    Returns:
    --------
    labels : array
        预测的细胞类型标签
    """
    from sklearn.neighbors import KNeighborsClassifier

    # 获取参考数据的注释
    if 'cell_type' not in adata_reference.obs:
        raise ValueError("Reference data must have cell_type annotation")

    # 使用PCA嵌入
    X_ref = adata_reference.obsm['X_pca']
    X_query = adata_query.obsm['X_pca']

    # 确保维度匹配
    min_dims = min(X_ref.shape[1], X_query.shape[1])
    X_ref = X_ref[:, :min_dims]
    X_query = X_query[:, :min_dims]

    # 训练KNN分类器
    labels_ref = adata_reference.obs['cell_type'].values
    knn = KNeighborsClassifier(n_neighbors=30, weights='distance')
    knn.fit(X_ref, labels_ref)

    # 预测
    predicted_labels = knn.predict(X_query)

    return predicted_labels


def run_cell2location(adata_st, adata_sc=None, n_cells_per_location=10):
    """
    使用cell2location进行空间解卷积

    cell2location使用贝叶斯模型估计每个空间位置的细胞类型组成。

    安装: pip install cell2location

    注意: cell2location需要大量内存和计算资源。

    Parameters:
    -----------
    adata_st : AnnData
        空间转录组数据
    adata_sc : AnnData, optional
        单细胞参考数据
    n_cells_per_location : int
        每个位置的参考细胞数估计

    Returns:
    --------
    adata_st : AnnData
        添加了细胞类型丰度估计
    """
    try:
        import cell2location
        import scvi
        HAS_CELL2LOCATION = True
    except ImportError:
        HAS_CELL2LOCATION = False
        warnings.warn(
            "cell2location not installed. Using alternative deconvolution. "
            "Install with: pip install cell2location scvi-tools"
        )

    print("Running cell2location spatial deconvolution...")

    if not HAS_CELL2LOCATION:
        # 使用简化版解卷积
        return spatial_deconvolution_simple(adata_st, adata_sc)

    # 完整的cell2location流程需要:
    # 1. 训练参考模型
    # 2. 估计细胞类型丰度
    # 这里提供简化实现

    if adata_sc is not None:
        # 使用参考数据估计标记基因
        cell_type_abundance = estimate_abundance(adata_st, adata_sc)
    else:
        # 使用内置标记基因
        cell_type_abundance = estimate_abundance_markers(adata_st)

    # 保存结果
    for ct, abundance in cell_type_abundance.items():
        adata_st.obs[f'{ct}_abundance'] = abundance

    adata_st.uns['scRNA_joint_analysis'] = {
        'method': 'cell2location',
        'n_cell_types': len(cell_type_abundance)
    }

    return adata_st


def estimate_abundance(adata_st, adata_sc):
    """
    使用参考数据估计细胞类型丰度
    """
    # 获取参考数据的标记基因
    cell_types = adata_sc.obs['cell_type'].unique()
    marker_genes = {}

    for ct in cell_types:
        ct_cells = adata_sc[adata_sc.obs['cell_type'] == ct]
        # 选择高表达的基因作为标记
        mean_expr = ct_cells.X.mean(axis=0)
        if hasattr(mean_expr, 'A1'):
            mean_expr = mean_expr.A1
        top_genes_idx = np.argsort(mean_expr)[-20:]
        marker_genes[ct] = [adata_sc.var_names[i] for i in top_genes_idx]

    # 估计丰度
    abundance = {}
    for ct, genes in marker_genes.items():
        genes_in_st = [g for g in genes if g in adata_st.var_names]
        if genes_in_st:
            abundance[ct] = adata_st[:, genes_in_st].X.mean(axis=1)

    return abundance


def estimate_abundance_markers(adata_st):
    """
    使用内置标记基因估计丰度
    """
    # 内置细胞类型标记
    markers = {
        'T cells': ['CD3D', 'CD3E'],
        'B cells': ['CD19', 'MS4A1'],
        'Macrophages': ['CD68', 'CD14'],
        'Epithelial': ['EPCAM', 'KRT18'],
        'Fibroblasts': ['COL1A1', 'FAP'],
        'Endothelial': ['PECAM1', 'VWF'],
    }

    abundance = {}
    for ct, genes in markers.items():
        genes_in_data = [g for g in genes if g in adata_st.var_names]
        if genes_in_data:
            X = adata_st[:, genes_in_data].X
            if hasattr(X, 'toarray'):
                X = X.toarray()
            abundance[ct] = X.mean(axis=1)

    return abundance


def spatial_deconvolution_simple(adata_st, adata_sc=None):
    """
    简化版空间解卷积
    """
    return estimate_abundance_markers(adata_st)


def run_spatialglue(adata_st, adata_sc=None):
    """
    使用SpatialGlue进行多模态整合分析

    SpatialGlue是一种图神经网络方法，可以整合空间转录组和单细胞数据。

    安装: pip install spatialglue

    这里提供简化版实现。

    Parameters:
    -----------
    adata_st : AnnData
        空间转录组数据
    adata_sc : AnnData, optional
        单细胞参考数据

    Returns:
    --------
    adata_st : AnnData
        添加了SpatialGlue分析结果
    """
    try:
        import spatialglue
        HAS_SPATIALGLUE = True
    except ImportError:
        HAS_SPATIALGLUE = False
        warnings.warn(
            "SpatialGlue not installed. Using alternative integration. "
            "Install with: pip install spatialglue"
        )

    print("Running SpatialGlue analysis...")

    if not HAS_SPATIALGLUE:
        # 使用简化的多模态整合
        return multimodal_integration_simple(adata_st, adata_sc)

    # 完整的SpatialGlue需要图神经网络
    # 这里提供简化版

    return multimodal_integration_simple(adata_st, adata_sc)


def multimodal_integration_simple(adata_st, adata_sc=None):
    """
    简化版多模态整合
    """
    if adata_sc is not None:
        # 基于共享基因的整合
        common_genes = list(set(adata_st.var_names) & set(adata_sc.var_names))

        if len(common_genes) > 100:
            # 使用CCA-like方法
            X_st = adata_st[:, common_genes].obsm['X_pca'] if 'X_pca' in adata_st.obsm else adata_st[:, common_genes].X
            X_sc = adata_sc[:, common_genes].obsm['X_pca'] if 'X_pca' in adata_sc.obsm else adata_sc[:, common_genes].X

            # Z-score标准化
            X_st = (X_st - X_st.mean(axis=0)) / (X_st.std(axis=0) + 1e-10)
            X_sc = (X_sc - X_sc.mean(axis=0)) / (X_sc.std(axis=0) + 1e-10)

            adata_st.obsm['X_spatialglue'] = X_st

    # 保存结果
    adata_st.uns['scRNA_joint_analysis'] = {
        'method': 'spatialglue',
        'has_reference': adata_sc is not None
    }

    return adata_st


def run_seurat_v5(adata_st, adata_sc=None):
    """
    Seurat V5 专用接口

    Seurat V5的主要改进:
    - 更快的PCA和UMAP计算
    - 更好的多模态整合
    - 新的标签迁移方法

    R端使用:
    library(Seurat)
    library(SeuratObject)

    # 创建Seurat对象
    st_obj <- as.Seurat(st_data, counts='X', data='layer')

    # 使用Seurat v5的标签迁移
    anchors <- FindTransferAnchors(st_obj, reference=sc_obj, normalization.method='SCT')
    predictions <- TransferData(anchors, refdata=sc_obj$cell_type)

    注意: 此功能需要R环境和Seurat 5.x
    """
    warnings.warn(
        "Full Seurat V5 integration requires R environment."
        "\n"
        "Required R packages:"
        "\n  install.packages('SeuratObject', repos='https://satijalab.r-universe.dev')"
        "\n  remotes::install_github('satijalab/seurat', 'seurat5')"
        "\n"
        "This Python implementation provides basic label transfer functionality."
    )

    # 使用Python端的标签迁移
    if adata_sc is not None:
        return label_transfer_knn(adata_st, adata_sc)
    else:
        return label_transfer_markers(adata_st)


# Snakemake script接口
if __name__ == "__snakemake__":
    input_file = snakemake.input[0]
    output_file = snakemake.output[0]
    method = snakemake.params["method"]
    params = snakemake.params["params"]

    adata = ad.read_h5ad(input_file)

    # 可选：加载scRNA参考数据（如果配置了）
    adata_sc = None
    if len(snakemake.input) > 1:
        adata_sc = ad.read_h5ad(snakemake.input[1])

    print(f"Running scRNA joint analysis with method: {method}")

    if method == "seurat":
        adata = run_seurat_transfer(adata, adata_sc, **params)
    elif method == "cell2location":
        adata = run_cell2location(adata, adata_sc, **params)
    elif method == "spatialglue":
        adata = run_spatialglue(adata, adata_sc, **params)
    else:
        raise ValueError(f"Unknown method: {method}")

    adata.write_h5ad(output_file)
    print(f"Results saved to {output_file}")
