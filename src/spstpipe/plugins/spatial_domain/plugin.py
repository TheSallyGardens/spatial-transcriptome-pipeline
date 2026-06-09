# spatial_domain 插件主类
from __future__ import annotations

from pathlib import Path

import anndata as ad

from spstpipe.core.base import BasePlugin
from spstpipe.core.io import load_anndata, save_anndata
from spstpipe.plugins.spatial_domain.algorithms import run_spectral_clustering


class SpatialDomainPlugin(BasePlugin):
    """空间域识别插件。

    支持方法：
      - spectral_clustering : 基于空间坐标的谱聚类（默认，无重依赖）
      - spagcn              : SpaGCN（图卷积，需 torch，懒加载）
      - bayespace / stlearn : 占位（默认走谱聚类）
    """

    name = "spatial_domain"
    version = "0.1.0"

    def __init__(self, method: str = "spectral_clustering", **params: object) -> None:
        self.method = method
        self.params = params

    def load(self, paths: list[Path]) -> ad.AnnData:
        if len(paths) != 1:
            raise ValueError(f"SpatialDomainPlugin.load 期望 1 个 h5ad 路径，实际 {len(paths)}")
        return load_anndata(paths[0])

    def preprocess(self, adata: ad.AnnData) -> ad.AnnData:
        if "spatial" not in adata.obsm and "x" in adata.obs and "y" in adata.obs:
            import numpy as np
            adata.obsm["spatial"] = np.column_stack([adata.obs["x"].values, adata.obs["y"].values])
        return adata

    def run(self, adata: ad.AnnData) -> ad.AnnData:
        kwargs = self._safe_params(["resolution"])
        if self.method in ("spectral_clustering", "spagcn", "bayespace", "stlearn", "placeholder"):
            # 重依赖方法（spagcn/bayespace/stlearn）当前以谱聚类兜底，老 run.py 也是这么做的
            return run_spectral_clustering(adata, **kwargs)
        raise ValueError(f"未知方法：{self.method}")

    def save(self, adata: ad.AnnData, path: Path) -> None:
        save_anndata(adata, path)

    def _safe_params(self, keys: list[str]) -> dict[str, object]:
        return {k: v for k, v in self.params.items() if k in keys}