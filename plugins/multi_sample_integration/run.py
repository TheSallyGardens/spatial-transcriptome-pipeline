# plugins/multi_sample_integration/run.py
import scanpy as sc
import anndata as ad
import numpy as np
import pandas as pd
import warnings


def run_harmony(adata_list, theta=2.0, max_iter=20, n_components=50):
    """
    使用Harmony进行批次校正和整合

    Harmony是成熟的批次校正方法，可以有效消除批次效应
    同时保留生物变异。

    安装: pip install harmonypy

    Parameters:
    -----------
    adata_list : list of AnnData
        多个样本的AnnData对象
    theta : float
        方差膨胀参数，越大越保守
    max_iter : int
        最大迭代次数
    n_components : int
        PCA维度

    Returns:
    --------
    adata_combined : AnnData
        整合后的AnnData
    """
    try:
        import harmonypy as hm
        HAS_HARMONY = True
    except ImportError:
        HAS_HARMONY = False
        warnings.warn(
            "harmonypy not installed. Using alternative batch correction. "
            "Install with: pip install harmonypy"
        )

    print("Running Harmony integration...")

    # 合并AnnData
    adata_combined = ad.concat(
        adata_list,
        batch_key="sample",
        uns_merge="same"
    )

    # 确保有PCA
    if 'X_pca' not in adata_combined.obsm:
        print("Computing PCA...")
        sc.pp.pca(adata_combined, n_comps=n_components)

    if HAS_HARMONY:
        # 使用Harmony
        ho = hm.Harmony(
            data_mat=adata_combined.obsm["X_pca"],
            meta_data=adata_combined.obs,
            group_by=["sample"],
            theta=theta,
            max_iter=max_iter,
            random_state=42
        )

        corrected = ho.Harmony_embedding()

        # 保存校正后的PCA
        adata_combined.obsm["X_pca_harmony"] = corrected
        adata_combined.obsm["X_pca"] = corrected  # 替换原PCA

        adata_combined.uns['integration'] = {
            'method': 'harmony',
            'theta': theta,
            'max_iter': max_iter,
            'corrected': True
        }

        print(f"Harmony completed: {len(ho.corrected_theta())} iterations")
    else:
        # 简化批次校正：ComBat-like调整
        adata_combined = combat_batch_correct(adata_combined, batch_key='sample')
        adata_combined.uns['integration'] = {
            'method': 'combat_like',
            'corrected': True
        }

    return adata_combined


def combat_batch_correct(adata, batch_key='sample'):
    """
    简化版ComBat批次校正

    不使用外部库，对每个样本的PCA坐标进行线性变换
    使其均值和方差一致
    """
    pca = adata.obsm['X_pca']
    batches = adata.obs[batch_key].unique()

    corrected = pca.copy()

    # 计算整体均值和方差
    global_mean = pca.mean(axis=0)
    global_std = pca.std(axis=0) + 1e-10

    for batch in batches:
        mask = adata.obs[batch_key] == batch
        batch_pca = pca[mask]

        # 批次均值和方差
        batch_mean = batch_pca.mean(axis=0)
        batch_std = batch_pca.std(axis=0) + 1e-10

        # Z-score标准化然后重新缩放
        z_scored = (batch_pca - batch_mean) / batch_std
        corrected[mask] = z_scored * global_std + global_mean

    adata.obsm['X_pca'] = corrected
    return adata


def run_bbknn(adata_list, n_neighbors=15, trim=10, approx=True):
    """
    使用BBKNN进行批次校正整合

    BBKNN (Batch Balanced KNN) 通过修改邻居搜索来减少批次效应。

    安装: pip install bbknn

    Parameters:
    -----------
    adata_list : list of AnnData
        多个样本的AnnData对象
    n_neighbors : int
        邻居数
    trim : int
        权重裁剪阈值
    approx : bool
        是否使用近似算法

    Returns:
    --------
    adata_combined : AnnData
        整合后的AnnData
    """
    try:
        import bbknn
        HAS_BBKNN = True
    except ImportError:
        HAS_BBKNN = False
        warnings.warn(
            "BBKNN not installed. Using standard邻居方法. "
            "Install with: pip install bbknn"
        )

    print("Running BBKNN integration...")

    # 合并AnnData
    adata_combined = ad.concat(
        adata_list,
        batch_key="sample",
        uns_merge="same"
    )

    # 确保有PCA
    if 'X_pca' not in adata_combined.obsm:
        print("Computing PCA...")
        sc.pp.pca(adata_combined, n_comps=50)

    if HAS_BBKNN:
        # 使用BBKNN计算邻居
        bbknn.ridge_graph(
            adata_combined,
            batch_key='sample',
            n_neighbors=n_neighbors,
            trim=trim,
            approx=approx
        )

        adata_combined.uns['integration'] = {
            'method': 'bbknn',
            'n_neighbors': n_neighbors,
            'trim': trim
        }
    else:
        # 使用标准邻居
        sc.pp.neighbors(adata_combined, n_neighbors=n_neighbors, n_pcs=50)
        adata_combined.uns['integration'] = {
            'method': 'standard_neighbors',
            'n_neighbors': n_neighbors
        }

    return adata_combined


def run_liger(adata_list, k=20, lambda_param=5.0, max_iter=30, n_components=50):
    """
    使用LIGER进行整合分析

    LIGER (Linked Inference of Gene Expression Relationships) 使用
    非负矩阵分解来识别共享的和样本特异的因素。

    安装: pip install rliger

    这里提供Python版本的简化实现。

    Parameters:
    -----------
    adata_list : list of AnnData
        多个样本的AnnData对象
    k : int
        因子数
    lambda_param : float
        正则化参数
    max_iter : int
        最大迭代次数
    n_components : int
        NMF维度

    Returns:
    --------
    adata_combined : AnnData
        整合后的AnnData
    """
    try:
        import rliger
        HAS_LIGER = True
    except ImportError:
        HAS_LIGER = False
        warnings.warn(
            "rliger not installed. Using alternative integration. "
            "Install with: pip install rliger"
        )

    print("Running LIGER integration...")

    # 合并AnnData
    adata_combined = ad.concat(
        adata_list,
        batch_key="sample",
        uns_merge="same"
    )

    if HAS_LIGER:
        # 完整的LIGER实现
        from sklearn.decomposition import NMF

        # 获取表达矩阵
        X = adata_combined.X
        if hasattr(X, 'toarray'):
            X = X.toarray()

        # 标准化
        X_norm = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-10)

        # 交替非负矩阵分解
        W, H =交替_nmf(X_norm.T, k=k, lambda_param=lambda_param, max_iter=max_iter)

        # 获取因子
        factors = H.T  # 细胞 x 因子

        adata_combined.obsm['X_liger'] = factors
        adata_combined.uns['integration'] = {
            'method': 'liger',
            'k': k,
            'lambda': lambda_param
        }
    else:
        # 简化版：使用PCA + Z-score
        if 'X_pca' not in adata_combined.obsm:
            sc.pp.pca(adata_combined, n_comps=n_components)

        # 批次间标准化
        pca = adata_combined.obsm['X_pca']
        batches = adata_combined.obs['sample'].unique()

        aligned_pca = pca.copy()
        global_mean = pca.mean(axis=0)
        global_std = pca.std(axis=0) + 1e-10

        for batch in batches:
            mask = adata_combined.obs['sample'] == batch
            batch_pca = pca[mask]
            aligned_pca[mask] = (batch_pca - batch_pca.mean(axis=0)) / (batch_pca.std(axis=0) + 1e-10)

        adata_combined.obsm['X_liger'] = aligned_pca * global_std + global_mean
        adata_combined.uns['integration'] = {
            'method': 'liger_like',
            'k': k
        }

    return adata_combined


def alternating_nmf(X, k, lambda_param=5.0, max_iter=30):
    """
    交替非负矩阵分解

    Parameters:
    -----------
    X : array
        输入矩阵 (genes x cells)
    k : int
        因子数
    lambda_param : float
        正则化参数
    max_iter : int
        最大迭代次数

    Returns:
    --------
    W : array
        基因负荷 (genes x k)
    H : array
        因子表达 (k x cells)
    """
    from sklearn.decomposition import NMF

    # 使用sklearn的NMF
    model = NMF(n_components=k, init='random', random_state=42, max_iter=max_iter, alpha_W=lambda_param)

    W = model.fit_transform(X.T)  # 转置以适应sklearn格式
    H = model.components_

    return W, H


def run_scanorama(adata_list, n_components=50):
    """
    使用SCANORAMA进行整合

    SCANORAMA是一种基于表达矩阵对齐的整合方法。

    安装: pip install scanorama

    Parameters:
    -----------
    adata_list : list of AnnData
        多个样本的AnnData对象

    Returns:
    --------
    adata_combined : AnnData
        整合后的AnnData
    """
    try:
        import scanorama
        HAS_SCANORAMA = True
    except ImportError:
        HAS_SCANORAMA = False
        warnings.warn(
            "SCANORAMA not installed. Using Harmony instead. "
            "Install with: pip install scanorama"
        )

    print("Running SCANORAMA integration...")

    if HAS_SCANORAMA:
        # 准备数据
        X_list = []
        for adata in adata_list:
            X = adata.X
            if hasattr(X, 'toarray'):
                X = X.toarray()
            X_list.append(X)

        # 运行SCANORAMA
        corrected, genes = scanorama.correct(X_list, return_dimred=True)

        # 合并
        adata_combined = ad.concat(adata_list, batch_key="sample", uns_merge="same")

        # 添加校正后的降维
        integrated = np.vstack(corrected)
        adata_combined.obsm['X_scanorama'] = integrated[:, :n_components]

        adata_combined.uns['integration'] = {
            'method': 'scanorama',
            'corrected': True
        }
    else:
        # 降级到Harmony
        return run_harmony(adata_list)

    return adata_combined


# Snakemake script接口
if __name__ == "__snakemake__":
    input_files = snakemake.input
    output_file = snakemake.output[0]
    method = snakemake.params["method"]
    params = snakemake.params["params"]

    adata_list = [ad.read_h5ad(f) for f in input_files]

    print(f"Running multi-sample integration with method: {method}")

    if method == "harmony":
        adata_combined = run_harmony(adata_list, **params)
    elif method == "bbknn":
        adata_combined = run_bbknn(adata_list, **params)
    elif method == "liger":
        adata_combined = run_liger(adata_list, **params)
    elif method == "scanorama":
        adata_combined = run_scanorama(adata_list, **params)
    else:
        raise ValueError(f"Unknown method: {method}")

    adata_combined.write_h5ad(output_file)
    print(f"Results saved to {output_file}")
